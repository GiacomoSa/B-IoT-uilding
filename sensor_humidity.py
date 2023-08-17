import random
import json
from MyMQTT import *
import time
import pandas as pd
from datetime import datetime

class Sensor():
        """docstring for Sensor"""
        def __init__(self,buildingID,floorID,roomID,sensorID,broker,port, measure, measure_unit):
            self.measure = measure
            self.measure_unit = measure_unit
            self.buildingID=buildingID
            self.floorID=floorID
            self.roomID=roomID
            self.sensorID=str(sensorID)
            self.topic='/'.join([self.buildingID,self.floorID,self.roomID,self.sensorID, self.measure])
            self.client=MyMQTT(self.sensorID,broker,port,None)
            self.__message={
                'buildingID':self.buildingID,
                'floorID':self.floorID,
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

            measure = self.measure
            temp = pd.read_csv(f"{measure}.csv")
            current_datetime = datetime.now()

            # Format the date as day/month/year
            formatted_date = current_datetime.strftime("%d/%m/")
            formatted_date += "2022"
            formatted_hour = current_datetime.strftime("%H:%M")
            if formatted_hour[-2:] == "00":
                temp = temp[temp['data'] == formatted_date]
                temp = temp[temp['ora (UTC)'] == formatted_hour]
                value = temp[f'{measure}'].values[0]
            else:
                lower_bound = formatted_hour[:2]
                lower_bound += ":00"
                temp = temp[temp['data'] == formatted_date]
                lower_bound = temp[temp['ora (UTC)'] == lower_bound]
                low_temp = float(lower_bound[f'{measure}'].values[0])
                value = round(random.uniform(low_temp, low_temp + 1), 2)

            return value

        def sendData(self):
            message=self.__message
            message['e'][0]['value']= self.getValue()
            message['e'][0]['timestamp']=str(time.time())
            self.client.myPublish(self.topic,json.dumps(message))
            print("Published!\n" + json.dumps(message) + "\n")

        def start (self):
            self.client.start()

        def stop (self):
            self.client.stop()

if __name__ == '__main__':
        conf=json.load(open("settings.json"))
        Sensors=[]
        buildingID=conf["baseTopic"]
        floorIDs=[str(i)  for i in range(1)]
        roomIDs=[str(i+1) for i in range(1)]
        broker=conf["broker"]
        port=conf["port"]
        s=0
        for floor in floorIDs:
            for room in roomIDs:
                sensor=Sensor(buildingID,floor,room,s,broker,port, "humidity", "%")
                Sensors.append(sensor)
                s+=1
        for sensor in Sensors:
            sensor.start()
        while True:
            for sensor in Sensors:
                sensor.sendData()
                time.sleep(1)