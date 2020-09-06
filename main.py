from flask import Flask, request, jsonify

import time
import requests
import json

import pymysql
import re


# make Chinese text clean
def clean_zh_text(text):
    # keep English, digital and Chinese
    comp = re.compile('[^A-Z^a-z^0-9^\u4e00-\u9fa5^\n^\r^()^!/~#$_^\s^\t^,，]')
    return comp.sub('', text)

conn = None
num = 0

app = Flask(__name__)



@app.route('/history')
def history():
    
    content = request.json
    
    pid = content.get('pid')
    
    try:
        with conn.cursor() as cursor:

            sql = f"SELECT product.name, product_price.price, product_price.datetime FROM product INNER JOIN product_price ON product.pid=product_price.pid WHERE product.pid = '{pid}'"
            cursor.execute(sql)
            result = cursor.fetchall()

            names = []
            prices = []
            datatimes = []
            for row in result:
                names.append(row[0])
                prices.append(row[1])
                datatimes.append(row[2])
            print(sql)
            print(len(result))

    except Exception as ex:
        print(ex)
        
    j = []
    for i in range(len(prices)):
        obj = {
            
            'name': names[i],
            'price': prices[i],
            'datetime': str(datatimes[i])#.strftime('%Y-%m-%d')
        }
        print(str(datatimes[i]))
        j.append(obj)

    return json.dumps(j)


@app.route('/search')
def search():
    
    content = request.json
    
    keyword = content.get('search')
    
    print('your search keyword:', keyword)
    
    try:
        with conn.cursor() as cursor:

            sql = f"SELECT pid, name, price FROM product WHERE name LIKE '%{keyword}%' ORDER BY price DESC"
            cursor.execute(sql)
            result = cursor.fetchall()

            names = []
            prices = []
            for row in result:
                names.append(row[1])
                prices.append(row[2])
            print(sql)
            print(len(result))

    except Exception as ex:
        print(ex)
        
    j = []
    for i in range(len(prices)):
        obj = {
            
            'name': names[i],
            'price': prices[i]
        }
        j.append(obj)

    return json.dumps(j)

@app.route('/crawl')
def crawl():
    
    global num
    num+=1
    
    content = request.json

    url = 'https://ecshweb.pchome.com.tw/search/v3.3/all/results'
    keyword = content.get('search')
    pages = num #1#data.get('totalPage')

    ls = []
    for p in range(pages):
        
        info = f'?q={keyword}&page={p+1}&sort=sale/dc'  
        res = requests.get(url + info)
        print(res, p+1)
        while res.status_code != 200:
            res = requests.get(url + info)
            print(res, p+1)
            time.sleep(2)
        data = json.loads(res.text)
        ls.append(data)

    prods_id = []
    prods_name = []
    prods_describe = []
    prods_price = []
    for p in ls:   
        for item in p.get('prods'):
            prods_id.append(item.get('Id'))
            prods_name.append(clean_zh_text(item.get('name')))
            prods_describe.append(clean_zh_text(item.get('describe')))
            #prods_describe.append(item.get('describe'))
            prods_price.append(item.get('price'))

    try:
        with conn.cursor() as cursor:

            sql = "SELECT pid, name, price FROM product"
            cursor.execute(sql)
            result = cursor.fetchall()

            pids = []
            prices = []
            for row in result:
                pids.append(row[0])
                prices.append(row[2])

            count_insert, count_update = 0, 0
            for p_pid,p_name,p_describe,p_price in zip(prods_id,prods_name,prods_describe,prods_price):
                ext = 0
                for pid,price in zip(pids,prices):

                    if p_pid == pid and p_price == price:
                        print('exists')
                        ext = 1
                        break;

                    if p_pid == pid and p_price != price:
                        print('update price & insert new price record')
                        ext = 1

                        sql_update = f"UPDATE product SET price = {p_price} WHERE pid = '{p_pid}'"
                        cursor.execute(sql_update)
                        sql_insert = f"INSERT INTO product_price (pid,price) VALUES ('{p_pid}','{p_price}')"
                        cursor.execute(sql_insert)
                        conn.commit()
                        
                        count_update+=1

                        break;

                if ext == 0:
                    print('insert new product')
                    sql = f"INSERT INTO product (pid, name, description, price) VALUES ('{p_pid}','{p_name}','{p_describe}','{p_price}')"
                    cursor.execute(sql)
                    sql_insert = f"INSERT INTO product_price (pid,price) VALUES ('{p_pid}','{p_price}')"
                    cursor.execute(sql_insert)
                    conn.commit()
                    
                    count_insert+=1

    #         sql = "INSERT INTO product (pid, name, description, price) VALUES (%s,%s,%s,%s)"
    #         records = gp[:]
    #         cursor.executemany(sql, records)
    
        cursor.close()
        
    except Exception as ex:
        print(ex)
        
        print(f'本次爬蟲->"{keyword}"  Insert:{count_insert}筆; Update:{count_update}筆。')

    return f'本次爬蟲->"{keyword}"  Insert:{count_insert}筆; Update:{count_update}筆。'



@app.route('/crawl_test')
def crawl_test():
    
    cg_pid = request.json.get('pid')
    cg_price = request.json.get('price')

    prods_id = [
        'DPAH2J-A9009CA2D',
        'DCAYQN-A900ARDVK',
        cg_pid
    ]
    prods_name = [
        'test01',
        'test02',
        'test03'
    ]
    prods_describe = [
        'test01',
        'test02',
        'test03'
    ]
    prods_price = [
        99999,
        88888,
        cg_price
    ]


    try:
        with conn.cursor() as cursor:

            sql = "SELECT pid, name, price FROM product"
            cursor.execute(sql)
            result = cursor.fetchall()

            pids = []
            prices = []
            for row in result:
                pids.append(row[0])
                prices.append(row[2])

            count_insert, count_update = 0, 0
            for p_pid,p_name,p_describe,p_price in zip(prods_id,prods_name,prods_describe,prods_price):
                ext = 0
                for pid,price in zip(pids,prices):

                    if p_pid == pid and p_price == price:
                        print('exists')
                        ext = 1
                        break;

                    if p_pid == pid and p_price != price:
                        print('update price & insert new price record')
                        ext = 1

                        sql_update = f"UPDATE product SET price = {p_price} WHERE pid = '{p_pid}'"
                        cursor.execute(sql_update)
                        sql_insert = f"INSERT INTO product_price (pid,price) VALUES ('{p_pid}','{p_price}')"
                        cursor.execute(sql_insert)
                        conn.commit()
                        
                        count_update+=1

                        break;

                if ext == 0:
                    print('insert new product')
                    sql = f"INSERT INTO product (pid, name, description, price) VALUES ('{p_pid}','{p_name}','{p_describe}','{p_price}')"
                    cursor.execute(sql)
                    sql_insert = f"INSERT INTO product_price (pid,price) VALUES ('{p_pid}','{p_price}')"
                    cursor.execute(sql_insert)
                    conn.commit()
                    
                    count_insert+=1

    #         sql = "INSERT INTO product (pid, name, description, price) VALUES (%s,%s,%s,%s)"
    #         records = gp[:]
    #         cursor.executemany(sql, records)
    
        cursor.close()
        
    except Exception as ex:
        print(ex)

    return f'本次爬蟲->"test"  Insert:{count_insert}筆; Update:{count_update}筆。'


def db_connection():
    
    global conn
    
    db_settings = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "60771008",
        "charset": "utf8",
        "db": "enzodb"
    }
    try:
        # 建立Connection物件
        conn = pymysql.connect(**db_settings)    
    except Exception as ex:
        print(ex)

            
        
def db_create_table():
    
    global conn
    
    try:
        # 建立Cursor物件
        with conn.cursor() as cursor:

            cursor.execute("DROP TABLE IF EXISTS product")
            cursor.execute("CREATE TABLE product (id INT AUTO_INCREMENT PRIMARY KEY, pid VARCHAR(100) CHARACTER SET utf8, name VARCHAR(255) CHARACTER SET utf8, description TEXT CHARACTER SET utf8, price INT) default character set utf8")   
        
            cursor.execute("DROP TABLE IF EXISTS product_price")
            cursor.execute("CREATE TABLE product_price (id INT AUTO_INCREMENT PRIMARY KEY, pid VARCHAR(100) CHARACTER SET utf8, price INT, datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP) default character set utf8")    
    
    except Exception as ex:
        print(ex)
        
    
    
if __name__ == '__main__':
    
    db_connection()
    #db_create_table()
    
    
    app.run(host='0.0.0.0',port=5001)