import requests
print(requests.get("http://127.0.0.1:8080/api/user").json())
print(requests.get("http://127.0.0.1:8080/api/user/1").json())
print(requests.get("http://127.0.0.1:8080/api/news").json())
print(requests.get("http://127.0.0.1:8080/api/news/1").json())
print(requests.get("http://127.0.0.1:8080/api/review").json())
print(requests.get("http://127.0.0.1:8080/api/review/1").json())