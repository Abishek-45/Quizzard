import requests

try:
    response = requests.post('http://127.0.0.1:8888/api/join-quiz/', json={"code" : "0110"})
    print(response.status_code)
    print(response.text)
except Exception as e:
    print("Error : ", e)
