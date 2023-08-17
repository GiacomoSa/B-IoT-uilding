import requests

if __name__ == '__main__':

    url = "http://127.0.0.1:9096/building"
    data = {
    "building_id": "b2",
    "building_type": "Museum",
    "rooms": [
      "A0",
      "A1",
      "A2",
      "B0",
      "B1",
      "Entrance"
    ]
    }

    r = requests.post(url, data)

    print(r)
    print(r.content)