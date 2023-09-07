import requests
import json

if __name__ == "__main__":

    url = "http://127.0.0.1:9095/building"
    payload = json.dumps({"prova": "you"})

    r = requests.post(url, payload)
    print(r.text)