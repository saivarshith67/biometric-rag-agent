import requests
BASE_URL = "https://7j0hq80w-8000.use2.devtunnels.ms/"

def start():
    return requests.get(BASE_URL)


def chat_with_bot(input : str):
    body = {"query" : input}
    response = requests.post(BASE_URL+"query", json=body)
    return response