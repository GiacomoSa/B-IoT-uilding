import random
import json
from MyMQTT import *
import time
import pandas as pd
from datetime import datetime
import os
class Sensor():
        """docstring for Sensor"""
        def __init__(self,buildingID,roomID,sensorID, measure, measure_unit):
            print(os.getcwd())
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
                low_temp = float(lower_bound['temperature'].values[0])
                value = round(random.uniform(low_temp, low_temp + 1), 2)

            return value

        def sendData(self):
            message=self.__message
            message['e'][0]['value']= self.getValue()
            message['e'][0]['timestamp']=str(time.time())
            self.client.myPublish(self.topic,json.dumps(message))
            print("Published!\n" + json.dumps(message) + "\n")
            print(f"Topic={self.topic}")

        def start (self):
            self.client.start()

        def stop (self):
            self.client.stop()



if __name__ == '__main__':
    # https://9aca-87-4-225-230.ngrok.io/


        #Io mi devo connettere al catalog e ricavare building e room, sensorID, topic, measure, broker, port
        sensors = json.load(open("sensors.json"))
        temp_sens=[]
        for sensor in sensors['sensors']:
            if sensor['measure'] == 'temperature':
                #class sensor wants buildingID,roomID,sensorID,broker,port, measure, measure_unit
                sensor=Sensor(buildingID=sensor['building_id'],
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
            if time.time() - start_send > 30:
                for sensor in temp_sens:
                    sensor.sendData()
                    start_send = time.time()
            if  time.time() - start_reg > 30:
                connector.registration()
                start_reg = time.time()