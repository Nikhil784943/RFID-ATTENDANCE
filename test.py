import requests

url = "http://127.0.0.1:5000/scan"
print(requests.post(url, json={"uid": "91285723"}).json())