import requests

# Примеры корректныз запросов
print(requests.get("http://127.0.0.1:8080/api/user").json())
print(requests.get("http://127.0.0.1:8080/api/user/1").json())
print(requests.get("http://127.0.0.1:8080/api/news").json())
print(requests.get("http://127.0.0.1:8080/api/news/1").json())
print(requests.get("http://127.0.0.1:8080/api/review").json())
print(requests.get("http://127.0.0.1:8080/api/review/1").json())
print(requests.post('http://localhost:8080/api/user', json={
    'email': '123@123.ru',
    'surname': "123",
    'name': '123',
    "age": '123',
    "gender": "123",
    "password": '123',
    "vk_url": "123"}).json())
