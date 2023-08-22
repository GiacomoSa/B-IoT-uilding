import random
import json
from MyMQTT import *
import time
import pandas as pd
from datetime import datetime
import requests

class Sensor():
        """docstring for Sensor"""
        def __init__(self,buildingID,roomID,sensorID, measure, measure_unit):
            self.conf = json.load(open("settings.json"))  # File contenente broker, porta e basetopic
            self.baseTopic = self.conf["baseTopic"]
            self.broker = self.conf["broker"]
            self.port = self.conf["port"]

            self.measure = measure
            self.measure_unit = measure_unit
            self.buildingID = f"Building_{buildingID}"
            self.roomID = f"Room_{roomID}"
            self.sensorID = f"Sensor_{str(sensorID)}"

            self.topic = '/'.join([self.baseTopic, self.buildingID, self.roomID, self.measure, self.sensorID])
            self.client = MyMQTT(self.sensorID, self.broker, self.port, None)
            self.__message = {
                'buildingID': self.buildingID,
                'roomID': self.roomID,
                'bn': self.sensorID,
                'e':
                    [
                        {
                            'n': self.measure,
                            'value': '',
                            'unit': self.measure_unit,
                            'timestamp': ''
                        },
                    ]
            }

        def getValue(self):

            value = random.randint(0,10)

            return value

        def sendData(self):
            message=self.__message
            message['e'][0]['value']= str(self.getValue())
            message['e'][0]['timestamp']=str(time.time())
            self.client.myPublish(self.topic,json.dumps(message))
            print("Published!\n" + json.dumps(message) + "\n")
            print(f"Topic={self.topic}")

        def start (self):
            self.client.start()

        def stop (self):
            self.client.stop()


if __name__ == '__main__':
    sensors = json.load(open("sensors.json"))
    temp_sens = []
    for sensor in sensors['sensors']:
        if sensor['measure'] == 'motion':
            # class sensor wants buildingID,roomID,sensorID,broker,port, measure, measure_unit
            sensor = Sensor(buildingID=sensor['building_id'],
                            roomID=sensor['room_id'],
                            sensorID=sensor['sensor_id'],
                            measure=sensor['measure'],
                            measure_unit=sensor['measure_unit'])
            temp_sens.append(sensor)
    for sensor in temp_sens:
        sensor.start()

    start_send = time.time()
    start_reg = time.time()
    while True:
        if time.time() - start_send > 1:
            for sensor in temp_sens:
                sensor.sendData()
                start_send = time.time()