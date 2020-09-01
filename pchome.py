
from flask import Flask, request, jsonify

import time
import requests
import json

import pymysql
import re

app = Flask(__name__)

@app.route('/')
def hello_world():
    
    content = request.json
    print(content)
    
    return 'Hello, World!'

    

    url = 'https://ecshweb.pchome.com.tw/search/v3.3/all/results'
    pages = 20#data.get('totalPage')

    ls = []
    for p in range(pages):
        info = f'?q=apple&page={p+1}&sort=sale/dc'

        res = requests.get(url + info)
        print(res, p+1)
        while res.status_code != 200:
            res = requests.get(url + info)
            print(res, p+1)
            time.sleep(2)
        data = json.loads(res.text)
        ls.append(data)


    # make Chinese text clean
    def clean_zh_text(text):
        # keep English, digital and Chinese
        comp = re.compile('[^A-Z^a-z^0-9^\u4e00-\u9fa5^\n^\r^()^!/~#$_^\s^\t^,，]')
        return comp.sub('', text)


    prods_id = []
    prods_name = []
    prods_describe = []
    prods_price = []

    for p in ls:   
        for item in p.get('prods'):
            prods_id.append(item.get('Id'))
            prods_name.append(item.get('name'))
            prods_describe.append(clean_zh_text(item.get('describe')))
            #prods_describe.append(item.get('describe'))
            prods_price.append(item.get('price'))


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




    try:
        # 建立Cursor物件
        with conn.cursor() as cursor:

            cursor.execute("DROP TABLE IF EXISTS product")
    #         cursor.execute("alter table product default character set utf8")
            cursor.execute("CREATE TABLE product (id INT AUTO_INCREMENT PRIMARY KEY, pid VARCHAR(100) CHARACTER SET utf8, name VARCHAR(255) CHARACTER SET utf8, description TEXT CHARACTER SET utf8, price INT) default character set utf8")   
    except Exception as ex:
        print(ex)




    try:
        # 建立Cursor物件
        with conn.cursor() as cursor:

            cursor.execute("DROP TABLE IF EXISTS product_price")
    #         cursor.execute("alter table product default character set utf8")
            cursor.execute("CREATE TABLE product_price (id INT AUTO_INCREMENT PRIMARY KEY, pid VARCHAR(100) CHARACTER SET utf8, price INT, datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP) default character set utf8")    
    except Exception as ex:
        print(ex)




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

                        break;

                if ext == 0:
                    print('insert new product')
                    sql = f"INSERT INTO product (pid, name, description, price) VALUES ('{p_pid}','{p_name}','{p_describe}','{p_price}')"
                    cursor.execute(sql)
                    sql_insert = f"INSERT INTO product_price (pid,price) VALUES ('{p_pid}','{p_price}')"
                    cursor.execute(sql_insert)

    #         sql = "INSERT INTO product (pid, name, description, price) VALUES (%s,%s,%s,%s)"
    #         records = gp[:]
    #         cursor.executemany(sql, records)

            conn.commit()
    except Exception as ex:
        print(ex)
    
    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001)