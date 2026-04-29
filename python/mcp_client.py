import requests
import json

# LM Studio local API
url = "http://localhost:1234/v1/chat/completions"

headers = {
    "Content-Type": "application/json"
}

data = {
    "model": "local-model",
    "messages": [
        {"role": "user", "content": "What genes are most expressed in Alzheimer's?"}
    ],
    "temperature": 0.7
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.json())
