import requests
import json

if __name__ == '__main__':
    # POST SU /building
    """
    url = "http://127.0.0.1:9095/building?username=mirko&type=owned"
    payload={
        "building": "prova"
    }
    r = requests.post(url, json.dumps(payload))
    print(r.text)
    """
    # PUT su /user
    url = "http://127.0.0.1:9095/user/building?username=mirko&type=observed"
    payload = {
        "building_id": "5",
        "username": "mirko"
    }
    r = requests.put(url, json.dumps(payload))
    print(r.text)



