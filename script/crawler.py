import requests
import json

f = open('/home/g60771008h/interview_demo/config/items.txt', "r", encoding='utf-8')
text = []
for line in f:
    
    line = line.strip()
    text.append(line)

for kw in text:
    
    json_dict = {
        'search': kw #apple banana orange
    }
    res = requests.get('http://127.0.0.1:5001/crawl', json=json_dict)

    print(res.text)