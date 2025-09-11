import requests
import json

url = "http://127.0.0.1:8000/apis/v1/summarize"
headers = {"Content-Type": "application/json"}
data = {"email_index": 0}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code != 200:
    print("Error occurred!")
else:
    print("Success!")