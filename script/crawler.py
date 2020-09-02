import requests
import json

f = open('config/items.txt', "r", encoding='utf-8')
text = []
for line in f:
    
    line = line.strip()
    text.append(line)

for kw in text:
    
    json_dict = {
        'search': kw #apple banana orange
    }
    res = requests.get('http://35.185.150.26:5001/crawl', json=json_dict)

    print(res.text)