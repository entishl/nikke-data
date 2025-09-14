import requests
import json

url = "http://localhost:8000/upload/"
file_path = '../input/ENTY.json'

with open(file_path, 'rb') as f:
    files = {'file': (file_path, f, 'application/json')}
    response = requests.post(url, files=files)

print(response.json())