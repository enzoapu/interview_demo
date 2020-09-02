import requests
import json
    
f = open('config/price_test.txt', "r", encoding='utf-8')
text = []
for line in f:
    
    line = line.strip()
    text.append(line)

for price in text:
    
    json_dict = {
        'pid': 'QBAB3F-A900A4ZT9',
        'price': price
    }
    res = requests.get('http://35.185.150.26:5001/crawl_test', json=json_dict)

    print(res.text)