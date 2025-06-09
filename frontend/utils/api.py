import requests
# BASE_URL = "http://localhost:8000/"
BASE_URL = "https://7j0hq80w-8000.use2.devtunnels.ms/"

def start():
    return requests.get(BASE_URL)


def chat_with_bot(user_input: str):
    body = {"query": user_input}
    headers = {"Content-Type": "application/json"}

    response = requests.post(BASE_URL + "query", json=body, headers=headers)

    if response.status_code == 200:
        return response.json()["message"]
    else:
        raise Exception(f"Request failed: {response.status_code} - {response.text}")