"""
A ogni room corrisponde un canale di TS, quindi dentro il JSON delle room abbiamo il diz con una API_key corrispondente
a ogni room.
"""

import requests
import random
import time
import json
from MyMQTT import *


class Control():
    exposed = True

    def __init__(self, baseTopic, broker, port, clientID): #notifier,

        # create an instance of paho.mqtt.client
        #self._paho_mqtt = PahoMQTT.Client(self.clientID, False)
        self.client = MyMQTT(clientID, broker, port, self)
        self.topic = ""

        with open("../Database/Buildings.json", 'r') as f:
            self.buildings = json.load(f)
        self.fields = {
            "temperature": "field1",
            "humidity": "field2",
            "particulate": "field3",
            "motion": "field4",
            "light": "field5",  # on/off
            "heating": "field6",  # on/off
        }


    def notify(self, topic, payload):

        # A new message is received
        topic = topic
        payload = json.loads(payload)

        elements = topic.split('/')
        measure = elements[-1]
        room_id = elements[-2].split('_')[-1]
        building_id = elements[-3].split('_')[-1]

        print("Message Received!")
        print()

        for building in self.buildings:
            if building["building_id"] == building_id:
                try:
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

                except KeyError as e:
                    print(f"Error {e}")

                break


    def start(self, topic):
        # manage connection to broker
        self.topic = topic
        self.client.start()
        self.client.mySubscribe(topic)

    def stop(self):
        self.client.stop()
        #self.client.stop_TS()


if __name__ == '__main__':

    with open("../settings.json", 'r') as f:
        settings = json.load(f)

    baseTopic = settings["baseTopic"]
    broker = settings["broker"]
    port = settings["port"]
    clientID = "TSconnector"

    thingspeak_control = Control(baseTopic=baseTopic, broker=broker, port=port, clientID=clientID)

    with open("../Database/Sensors.json", "r") as f:
        all_sensors = json.load(f)

    '''
    for sensor_list in all_sensors:
        for sensor in sensor_list["sensors"]:
            building_id = f"Building_{sensor['building_id']}"
            room_id = f"Room_{sensor['room_id']}"
            measure = sensor["measure"]
            topic = '/'.join([baseTopic, building_id, room_id, measure])
            thingspeak_control.mySubscribe(topic)
    '''
    topic = '/'.join([baseTopic, '#'])
    #topic = "BuIoTilding/Building_0/Room_Bathroom/motion"
    thingspeak_control.stop()
    thingspeak_control.start(topic)

    while True:
        cnt = 0

