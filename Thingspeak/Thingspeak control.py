"""
A ogni room corrisponde un canale di TS, quindi dentro il JSON delle room abbiamo il diz con una API_key corrispondente
a ogni room.
"""

import requests
import random
import time
import json
from MyMQTT import *


class Control(MyMQTT):

    def __init__(self, clientID, broker, port, notifier):
        super().__init__(clientID, broker, port, notifier)
        self.notifier = self
        with open("../Database/Buildings.json", 'r') as f:
            self.buildings = json.load(f)

        self.fields = {
            "temperature": "field1",
            "humidity": "field2",
            "PM": "field3",
            "motion": "field4",
            "light": "field5",  # on/off
            "heating": "field6",  # on/off
        }

    def notify(self, topic: str, payload):
        # extract meas from topic
        elements = topic.split('/')
        measure = elements[-1]
        room_id = elements[-2].split('_')[-1]
        building_id = elements[-3].split('_')[-1]

        for building in self.buildings:
            if building["building_id"] == building_id:
                keys_dict = building["API_keys"]
                API_KEY = keys_dict[room_id]
                BASE_URL = f"https://api.thingspeak.com/update?api_key={API_KEY}"
                field = self.fields[measure]

                # get value
                value_to_send = float(payload['e'][0]['value'])

                url = f"{BASE_URL}&{field}={value_to_send}"
                print(url)

                # Invia la richiesta HTTP per inviare i dati
                response = requests.get(url)

                if response.status_code == 200:
                    print("Dati inviati con successo a ThingSpeak")
                else:
                    print("Errore nell'invio dei dati a ThingSpeak")

                break


if __name__ == '__main__':

    with open("../settings.json", 'r') as f:
        settings = json.load(f)

    baseTopic = settings["baseTopic"]
    broker = settings["broker"]
    port = settings["port"]
    clientID = "TScontrol"

    thingspeak_control = Control(broker=broker, port=port, clientID=clientID, notifier="")

    with open("../Database/Sensors.json", "r") as f:
        all_sensors = json.load(f)

    for sensor_list in all_sensors:
        for sensor in sensor_list["sensors"]:
            building_id = f"Building_{sensor['building_id']}"
            room_id = f"Room_{sensor['room_id']}"
            measure = sensor["measure"]
            topic = '/'.join([baseTopic, building_id, room_id, measure])
            thingspeak_control.mySubscribe(topic)

    while True:
        pass

'''
"Bedroom": "",
            "Bathroom2":  "",
            "Kitchen":  "",
            "LivingRoom": ""
'''
