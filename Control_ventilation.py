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

class ventilation_control():
    exposed = True

    def __init__(self, clientID, baseTopic, buildingID, roomID, sensorID, measure, broker, port, threshold):  # notifier,
        self.control_type = 'ventilation'
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
        # self.notifier = notifier
        self.clientID = clientID
        # TODO forse ho bisogno di due topic, uno a cui mi iscrivo e uno su cui pubblico
        self.sub_topic ='/'.join([self.baseTopic, self.buildingID ,self.roomID, self.measure, self.sensorID])
        self._isSubscriber = True
        self.pub_topic = '/'.join([self.baseTopic, self.buildingID ,self.roomID, self.control_type])

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, False)

        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.broker, rc))

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

    def Breakpoints(self, C_P):
        if C_P <= 54:
            BP_LO = 0
            BP_HI = 54
            I_LO = 0
            I_HI = 50
            category = "Good"
        elif 55 <= C_P <= 154:
            BP_LO = 55
            BP_HI = 154
            I_LO = 51
            I_HI = 100
            category = "Moderate"
        elif 155 <= C_P <= 254:
            BP_LO = 155
            BP_HI = 254
            I_LO = 101
            I_HI = 150
            category = "Unhealty for sensitive groups"
        elif 255 <= C_P <= 354:
            BP_LO = 255
            BP_HI = 354
            I_LO = 151
            I_HI = 200
            category = "Unhealty"
        elif 355 <= C_P <= 424:
            BP_LO = 355
            BP_HI = 424
            I_LO = 201
            I_HI = 300
            category = "Very unhealty"
        elif 425 <= C_P <= 504:
            BP_LO = 425
            BP_HI = 504
            I_LO = 301
            I_HI = 400
            category = "Hazardous"
        elif 505 <= C_P <= 604:
            BP_LO = 505
            BP_HI = 604
            I_LO = 401
            I_HI = 500
            category = "Hazardous"
        else:
            raise ValueError
        return BP_LO, BP_HI, I_LO, I_HI, category


    def AIQ(self, C_P):
        # C_P is the rounded concentration of pollutant p
        # BP_HI is the breakpoint greater than or equal to C_P
        # BP_LO is the breakpoint less than or equal to C_P
        # I_HI = the AQI value corresponding to BP_HI
        # I_LO = the AQI value corresponding to BP_LO
        BP_LO, BP_HI, I_LO, I_HI, category = self.Breakpoints(C_P)
        AIQ = int((I_HI - I_LO) / (BP_HI - BP_LO) * (C_P - BP_LO) + I_LO)
        return AIQ  # , category

    def myOnMessageReceived(self, paho_mqtt, userdata, rcv_msg):
        # A new message is received
        # TODO, controllo la temperatura che ricevo se rispetta threshold accendo altrimenti spengo
        # TODO, fare double check se è già acceso
        payload = json.loads(rcv_msg.payload)
        measure_to_check = float(payload['e'][0]['value'])
        AIQ = self.AIQ(measure_to_check)
        if AIQ <= self.threshold:
            if self.status == 1:  # spento
                self.status = 0  # acceso
                pub_msg = f"{self.measure} below threashold, {self.control_type} turned on"
                self.myPublish(self.pub_topic, pub_msg)
            else:
                pub_msg = f"{self.measure} below threashold, {self.control_type} already on"
                self.myPublish(self.pub_topic, pub_msg)
        else:
            if self.status == 0:  # acceso
                self.status = 1  # spento
                pub_msg = f"{self.measure} above threashold, {self.control_type} turned off"
                self.myPublish(self.pub_topic, pub_msg)
            else:
                pub_msg = f"{self.measure} above threashold, {self.control_type} already off"
                self.myPublish(self.pub_topic, pub_msg)


    def myPublish(self, topic, pub_msg):

        # if needed, you can do some computation or error-check before publishing
        print("publishing '%s' with topic '%s'" % (pub_msg, topic))
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, pub_msg, 2)