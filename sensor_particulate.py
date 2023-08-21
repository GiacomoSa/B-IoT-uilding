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
            self.buildingID=f"Building_{buildingID}"
            self.roomID=f"Room_{roomID}"
            self.sensorID=f"Sensor_{str(sensorID)}"

            self.topic='/'.join([self.baseTopic, self.buildingID,self.roomID, self.measure, self.sensorID])
            self.client=MyMQTT(self.sensorID,self.broker,self.port,None)
            self.__message={
                'buildingID':self.buildingID,
                'roomID':self.roomID,
                'bn':self.sensorID,
                'e':
                    [
                        {
                            'n': self.measure,
                            'value':'',
                            'unit': self.measure_unit,
                            'timestamp':''
                        },
                        ]
                }

        def getValue(self):
            value = random.randint(400, 1000)
            return value

        def sendData(self):
            message=self.__message
            message['e'][0]['value'] = float(self.getValue())
            message['e'][0]['timestamp']=str(time.time())
            self.client.myPublish(self.topic , json.dumps(message))
            print("Published!\n" + json.dumps(message) + "\n")
            print(f"Topic={self.topic}")

        def start (self):
            self.client.start()

        def stop (self):
            self.client.stop()


if __name__ == '__main__':
        conf=json.load(open("Connector/settings.json")) #File contenente broker, porta e basetopic
        #Io mi devo connettere al catalog e ricavare building e room, sensorID, topic, measure, broker, port
        Sensors=[]
        baseTopic=conf["baseTopic"]
        BuildingID=[str(i)  for i in range(1)]
        roomIDs=[f"{BuildingID[i]}_{i+1}" for i in range(len(BuildingID))]
        broker=conf["broker"]
        port=conf["port"]
        s=0
        for building in BuildingID:
            for room in roomIDs:
                #class sensor wants buildingID,roomID,sensorID,broker,port, measure, measure_unit
                sensor=Sensor(buildingID=building,
                              roomID=room,
                              sensorID=s,
                              measure="particulate",
                              measure_unit="ppm")
                Sensors.append(sensor)
                s+=1
        for sensor in Sensors:
            sensor.start()
        while True:
            for sensor in Sensors:
                sensor.sendData()
                time.sleep(5)