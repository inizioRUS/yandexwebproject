import requests
import urllib3

urllib3.disable_warnings()
print(requests.get("https://79.143.30.45/api/user", verify=False).json())
print(requests.get("https://79.143.30.45/api/user/1", verify=False).json())
print(requests.get("https://79.143.30.45/api/news", verify=False).json())
print(requests.get("https://79.143.30.45/api/news/1", verify=False).json())
print(requests.get("https://79.143.30.45/api/review", verify=False).json())
print(requests.get("https://79.143.30.45/api/review/1", verify=False).json())
