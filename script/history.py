import requests
import json

json_dict = {
    'pid': 'QBAB3F-A900A4ZT9'
}
res = requests.get('http://35.185.150.26:5001/history', json=json_dict)

j = json.loads(res.text)

product_name = []
product_price = []
datetime = []
for p in j:
    product_name.append(p.get('name'))
    product_price.append(p.get('price'))
    datetime.append(p.get('datetime'))

if len(product_name):
    for name,price,dt in zip(product_name,product_price,datetime):
        print("Name:{0}\nPrice:{1}\nDatetime:{2}\n-------------------------------".format(name,price,dt))
else:
    print("not found.")