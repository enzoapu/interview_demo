import requests
import json

json_dict = {
    'search': '藍芽' #apple banana orange
}
res = requests.get('http://35.185.150.26:5001/search', json=json_dict)

j = json.loads(res.text)

product_name = []
product_price = []
for p in j:
    product_name.append(p.get('name'))
    product_price.append(p.get('price'))

if len(product_name):
    i = 0
    for name,price in zip(product_name,product_price):
        i+=1
        print("{0}\nName:{1}\nPrice:{2}\n-------------------------------".format(i,name,price))
else:
    print("not found.")