'''
 is a control strategy that helps to maintain certain parameter levels under
the chosen limits. It is an MQTT publisher and subscriber that retrieves data coming from the
sensors and according to them gives the appropriate response
'''

import json
import random
import requests
import sys
import cherrypy
import paho.mqtt.client as PahoMQTT
import time

class lighting_control():
    exposed = True

    def __init__(self, clientID, baseTopic, buildingID, roomID, sensorID, measure, broker, port, threshold): #notifier,
        self.control_type = 'lighting'
        self.buildingID = f"Building_{buildingID}"
        self.roomID = f"Room_{roomID}"
        self.sensorID = f"Sensor_{str(sensorID)}"
        self.baseTopic = baseTopic
        self.measure = measure
        self.threshold = threshold
        # status = 0 if heating turned on, status = 1 if turned off
        self.status = 1

        self.broker = broker
        self.port = port
        #self.notifier = notifier
        self.clientID = clientID
        #TODO forse ho bisogno di due topic, uno a cui mi iscrivo e uno su cui pubblico
        self.sub_topic='/'.join([self.baseTopic, self.buildingID,self.roomID, self.measure, self.sensorID])
        self._isSubscriber = True
        self.pub_topic = '/'.join([self.baseTopic, self.buildingID,self.roomID, self.control_type])

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, False)

        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.broker, rc))

    def myOnMessageReceived(self, paho_mqtt, userdata, rcv_msg):
        # A new message is received
        #TODO, controllo la temperatura che ricevo se rispetta threshold accendo altrimenti spengo
        #TODO, fare double check se è già acceso
        payload = json.loads(rcv_msg.payload)
        measure_to_check = float(payload['e'][0]['value'])
        if measure_to_check == 0.0:
            # status = 0 if on, status = 1 if off
            if self.status == 0: #se acceso
                self.status = 1 #lo spengo
                pub_msg = f"{self.measure} equal to zero, {self.control_type} turned off"
                self.myPublish(self.pub_topic, pub_msg)
            else: #se già spento
                pub_msg = f"{self.measure} equal to zero, {self.control_type} turned off"
                self.myPublish(self.pub_topic, pub_msg)
        else: #se ci sta gente
            if self.status == 1: #se acceso, lo lascio acceso
                pub_msg = f"{self.measure} not zero, {self.control_type} already on"
                self.myPublish(self.pub_topic, pub_msg)
            else:
                self.status = 1  # se spento lo accenso
                pub_msg = f"{self.measure} not zero, {self.control_type} turned on"
                self.myPublish(self.pub_topic, pub_msg)


    def myPublish(self, topic, pub_msg):

        # if needed, you can do some computation or error-check before publishing
        print("publishing '%s' with topic '%s'" % (pub_msg, topic))
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, pub_msg, 2)

    def mySubscribe(self):
        # if needed, you can do some computation or error-check before subscribing
        print("subscribing to %s" % (self.sub_topic))
        # subscribe for a topic
        self._paho_mqtt.subscribe(self.sub_topic, 2)
        # just to remember that it works also as a subscriber
        self._isSubscriber = True

    def start(self):
        # manage connection to broker
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()
        if self._isSubscriber:
            self.mySubscribe()

    def stop(self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber
            self._paho_mqtt.unsubscribe(self.sub_topic)

        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()



def registration(setting_file, service_file):  # IN ORDER TO REGISTER ON THE RESOURCE CATALOG
    with open(setting_file, "r") as f1:
        conf = json.loads(f1.read())

    with open(service_file, "r") as f2:
        conf_service = json.loads(f2.read())
    requeststring = 'http://' + conf_service['ip_address_service'] + ':' + conf_service[
        'ip_port_service'] + '/rooms_name_owner'
    r = requests.get(requeststring)
    print("INFORMATION FROM SERVICE CATALOG RECEIVED!\n")
    print(r.text)
    print("Available rooms and owners:\n " + r.text + "\n")
    owner = input("Which owner? ")
    room = input("\nWhich room? ")

    requeststring = 'http://' + conf_service['ip_address_service'] + ':' + conf_service[
        'ip_port_service'] + '/room_info?room=' + room + '&owner=' + owner
    r = requests.get(requeststring)
    print("INFORMATION OF RESOURCE CATALOG (room) RECEIVED!\n")  # PRINT FOR DEMO

    rc = json.loads(r.text)
    rc_ip = rc["ip_address"]
    rc_port = rc["ip_port"]
    poststring = 'http://' + rc_ip + ':' + rc_port + '/device'
    rc_basetopic = rc["base_topic"]
    rc_broker = rc["broker"]
    rc_port = rc["broker_port"]
    rc_owner = rc["owner"]

    sensor_model = conf["sensor_model"]

    requeststring = 'http://' + conf_service['ip_address_service'] + ':' + conf_service[
        'ip_port_service'] + '/base_topic'
    sbt = requests.get(requeststring)

    service_b_t = json.loads(sbt.text)
    topic = []
    body = []
    index = 0
    for i in conf["sensor_type"]:
        print(i)
        topic.append(service_b_t + '/' + rc_owner + '/' + rc_basetopic + "/" + i + "/" + conf["sensor_id"])
        body_dic = {
            "sensor_id": conf['sensor_id'],
            "sensor_type": conf['sensor_type'],
            "owner": rc["owner"],
            "measure": conf["measure"][index],
            "end-points": {
                "basetopic": service_b_t + '/' + rc_owner + '/' + rc_basetopic,
                "complete_topic": topic,
                "broker": rc["broker"],
                "port": rc["broker_port"]
            }
        }
        body.append(body_dic)
        requests.post(poststring, json.dumps(body[index]))
        print("REGISTRATION TO RESOURCE CATALOG (room) DONE!\n")  # PRINT FOR DEMO

        index = index + 1


if __name__ == "__main__":
    conf = json.load(open("Connector/settings.json"))  # File contenente broker, porta e basetopic
    # Io mi devo connettere al catalog e ricavare building e room, sensorID, topic, measure, broker, port
    Sensors = []
    baseTopic = conf["baseTopic"]
    BuildingID = [str(i) for i in range(1)]
    roomIDs = [f"{BuildingID[i]}_{i + 1}" for i in range(len(BuildingID))]
    broker = conf["broker"]
    port = conf["port"]
    # I need clientID, baseTopic, buildingID, roomID, measure, broker, port, notifier, threshold
    heating_control = lighting_control(clientID='Prova_Heating',
                                      baseTopic=baseTopic,
                                      buildingID=BuildingID[0],
                                      roomID=roomIDs[0],
                                      sensorID=0,
                                      measure='motion',
                                      broker=broker,
                                      port=port,
                                      threshold=30.0)
    heating_control.stop()
    heating_control.start()
    a = 0
    while (a < 30):
        a += 1
        time.sleep(5)

    heating_control.stop()