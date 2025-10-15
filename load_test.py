import requests

url = "http://localhost:8000/books"
headers = {"x-api-key": "supersecretkey123"}

for i in range(105):
    r = requests.get(url, headers=headers)
    print(i+1, r.status_code)
