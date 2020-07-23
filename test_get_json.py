# Author:peter young
import requests

url="http://127.0.0.1:5000/getjson"

r = requests.get(url)

print(r.status_code)

import json

for row in json.loads(r.text):
    print(row)