import random
import json
from MyMQTT import *
import time
import pandas as pd
from datetime import datetime
import requests

class Sensor():
        """docstring for Sensor"""
        def __init__(self,base_topic,buildingID,roomID,sensorID,broker,port, measure, measure_unit):
            self.measure = measure
            self.measure_unit = measure_unit
            self.buildingID=f"Building_{buildingID}"
            self.roomID=f"Room_{roomID}"
            self.sensorID=f"Sensor_{str(sensorID)}"
            self.baseTopic = base_topic
            self.topic='/'.join([self.baseTopic, self.buildingID,self.roomID, self.measure, self.sensorID])
            self.client=MyMQTT(self.sensorID,broker,port,None)
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


def registration(setting_file, service_file):  # IN ORDER TO REGISTER ON THE RESOURCE CATALOG
    with open(setting_file, "r") as f1:
        conf = json.loads(f1.read())

    with open(service_file, "r") as f2:
        conf_service = json.loads(f2.read())
    #You need an ip address for this service, as well as a port
    #TODO sostituire rooms name owner con stringa che permette di avere tutti i buildings e tutte le rooms
    requeststring = 'http://' + conf_service['ip_address_service'] + ':' + conf_service['ip_port_service'] + '/rooms_name_owner'
    r = requests.get(requeststring)
    print("INFORMATION FROM SERVICE CATALOG RECEIVED!\n")
    print(r.text)
    print("Available buildings and rooms:\n " + r.text + "\n")
    building = input("Which building? ") #Select the building
    room = input("\nWhich room? ") #Select the room
    #TODO Select the owner and the room, in our case it won't be the owner but the building, as well as the measurement?
    requeststring = 'http://' + conf_service['ip_address_service'] + ':' + conf_service[
        'ip_port_service'] + '/room_info?room=' + room + '&building=' + building
    r = requests.get(requeststring)
    print("INFORMATION OF RESOURCE CATALOG (room) RECEIVED!\n")  # PRINT FOR DEMO

    rc = json.loads(r.text)
    rc_ip = rc["ip_address"]
    rc_port = rc["ip_port"]
    poststring = 'http://' + rc_ip + ':' + rc_port + '/device'
    rc_basetopic = rc["base_topic"]
    rc_broker = rc["broker"]
    rc_port = rc["broker_port"]

    requeststring = 'http://' + conf_service['ip_address_service'] + ':' + conf_service[
        'ip_port_service'] + '/base_topic'
    sbt = requests.get(requeststring)

    service_b_t = json.loads(sbt.text)
    topic = []
    body = []
    index = 0
    topic.append(service_b_t + '/' + '/' + rc_basetopic + "/" + "/" + conf["sensor_id"])
    body_dic = {
        "sensor_id": conf['sensor_id'],
        "sensor_type": conf['sensor_type'],
        "owner": rc["owner"],
        "measure": conf["measure"][index],
        "end-points": {
            "basetopic": service_b_t + '/' + '/' + rc_basetopic,
            "complete_topic": topic,
            "broker": rc["broker"],
            "port": rc["broker_port"]
        }
    }
    body.append(body_dic)
    requests.post(poststring, json.dumps(body))
    print("REGISTRATION TO RESOURCE CATALOG (room) DONE!\n")  # PRINT FOR DEMO

    return rc_basetopic, conf["sensor_type"], conf["sensor_id"], topic, conf[
        "measure"], rc_broker, rc_port, rc["owner"]

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
                sensor=Sensor(base_topic=baseTopic,
                              buildingID=building,
                              roomID=room,
                              sensorID=s,
                              broker=broker,
                              port=port,
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