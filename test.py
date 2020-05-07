import requests
print(requests.get("https://twodyesbots.herokuapp.com/api/user").json())
print(requests.get("https://twodyesbots.herokuapp.com/api/user/1").json())
print(requests.get("https://twodyesbots.herokuapp.com/api/news").json())
print(requests.get("https://twodyesbots.herokuapp.com/api/news/1").json())
print(requests.get("https://twodyesbots.herokuapp.com/api/review").json())
print(requests.get("https://twodyesbots.herokuapp.com/api/review/1").json())