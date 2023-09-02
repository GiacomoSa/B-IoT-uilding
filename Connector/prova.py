import requests
import json

if __name__ == "__main__":

    url = "http://127.0.0.1:9094/Data/sensor?building_id=0&room_id=Kitchen"

    r = requests.get(url)
    print(r.text)