import requests

try:
    response = requests.get('http://127.0.0.1:8888/api/data/')
    print(response.status_code)
    print(response.headers)
    print(response.text)
except Exception as e:
    print("Error : ", e)