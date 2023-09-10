'''
is a control strategy that manages how crowded each room is.It works as
an MQTT subscriber to receive alerts from a people counter sensor and MQTT publisher to send
notifications to the user
'''

import json
import random
import requests
import sys
import cherrypy
import paho.mqtt.client as PahoMQTT
import time
import datetime

class lighting_control():
    exposed = True

    def __init__(self, controlID, baseTopic, buildingID, roomID, control_type, broker, port, threshold): #notifier,
        self.broker = broker
        self.port = port

        self.control_ID = controlID
        self.control_type = control_type
        self.measure = self.get_measure()
        self.buildingID = f"Building_{buildingID}"
        self.roomID = f"Room_{roomID}"
        self.baseTopic = baseTopic

        self.threshold = threshold
        self.time_schedule = {}
        self.time_schedule['on'] = "8"
        self.time_schedule['off'] = "17"

        self._isSubscriber = True
        self.sub_topic = '/'.join([self.baseTopic, self.buildingID, self.roomID, self.measure])
        self.pub_topic = '/'.join([self.baseTopic, self.buildingID, self.roomID, self.control_type])

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(controlID, False)
        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived


    def get_measure(self):
        control_types = json.load(open("controls.json"))
        return control_types[f'{self.control_type}']


    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.broker, rc))

    def time_control(self):
        actual_hour=int(datetime.datetime.now().strftime("%#H")) # '#' is used to remove the leading zero, it owrks only for windows, for unix use '-'
        if actual_hour>int(self.time_schedule['on']) or actual_hour>int(self.time_schedule['off']):
            return True
        else:
            return False

    def myOnMessageReceived(self, paho_mqtt, userdata, rcv_msg):
        # A new message is received
        #TODO, controllo la temperatura che ricevo se rispetta threshold accendo altrimenti spengo
        #TODO, fare double check se è già acceso
        payload = json.loads(rcv_msg.payload)
        measure_to_check = float(payload['e'][0]['value'])
        if self.time_control():
            if measure_to_check >= self.threshold:
                    pub_msg = f"Warning, People level above threashold!"
                    self.myPublish(self.pub_topic, pub_msg)

            else:
                pub_msg = f"People level below threashold, everything fine"
                self.myPublish(self.pub_topic, pub_msg)
        else:
            pub_msg = f"{self.control_type} control cannot be used during this time period"
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

if __name__ == "__main__":
    conf = json.load(open("../Connector/settings.json"))  # File contenente broker, porta e basetopic
    baseTopic = conf["baseTopic"]
    broker = conf["broker"]
    port = conf["port"]

    controls = json.load(open("actuators.json"))
    heat_controls = []
    for control in controls:
        if control['control_type'] == "people_level":
            heating_control = lighting_control(
                baseTopic=baseTopic,
                broker=broker,
                port=port,
                controlID=control['control_id'],
                buildingID=control['building_id'],
                roomID=control['room_id'],
                control_type=control['control_type'],
                threshold=30.0)
            heat_controls.append(heating_control)
    for control in heat_controls:
        control.stop()
        control.start()
    a = 0
    while (a < 30):
        a += 1
        time.sleep(5)
    for control in heat_controls:
        control.stop()