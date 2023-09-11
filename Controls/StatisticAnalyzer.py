import json
from MyMQTT import *
import numpy as np
import requests


# subscribe a tutti i sensori esistenti leggendoli dal json
# calcoliamo:
#   media generica
#   AQI
#   HUMIDEX
#

class StatisticAnalyzer:
    exposed = True

    def __init__(self, baseTopic, broker, port, clientID):  # notifier,
        self.broker = broker
        self.port = port

        self.clientID = clientID
        # self.measure = measure
        # self.control_type = self.get_controltype(self.measure)
        self.baseTopic = baseTopic

        self._isSubscriber = True

        # create an instance of paho.mqtt.client
        self.client = MyMQTT(clientID, broker, port, self)
        self.topic = ""

        # last values
        self.timegap = 30
        self.lastT = []
        self.lastH = []
        self.lastP = []
        self.lastM = []

        self.hourly_average_T = 0.0
        self.hourly_average_H = 0.0
        self.hourly_average_P = 0.0
        self.hourly_average_M = 0.0

    def start(self, topic):
        # manage connection to broker
        self.topic = topic
        self.client.start()
        self.client.mySubscribe(topic)

    def stop(self):
        self.client.stop()
        # self.client.stop_TS()

    def notify(self, topic, payload):
        # A new message is received
        # TODO, controllo la temperatura che ricevo se rispetta threshold accendo altrimenti spengo
        # TODO, fare double check se è già acceso
        topic = topic

        elements = topic.split('/')
        measure = elements[-1]
        room_id = elements[-2].split('_')[-1]
        building_id = elements[-3].split('_')[-1]

        # get TS code
        with open("../Database/Buildings.json", "r") as f:
            building_list = json.load(f)

        TS_key = ""
        for buil in building_list:
            if buil["building_id"] == building_id:
                keys = buil["API_keys"]
                TS_key = keys[room_id]
                break

        payload = json.loads(payload)
        measure_to_check = float(payload['e'][0]['value'])

        if measure == 'temperature':
            self.lastT.append(measure_to_check)
            HUMIDEX = self.HUMIDEX()
            self.hourly_average_T = self.average(self.lastT, self.hourly_average_T)
            # send HUMIDEX to thingSpeak
            BASE_URL = f"https://api.thingspeak.com/update?api_key={TS_key}"
            field = "field7"
            url = f"{BASE_URL}&{field}={HUMIDEX}"
            response = requests.get(url)

        elif measure == 'humidity':
            self.lastH.append(measure_to_check)
            HUMIDEX = self.HUMIDEX()
            self.hourly_average_H = self.average(self.lastH, self.hourly_average_H)
            # send HUMIDEX to thingSpeak
            BASE_URL = f"https://api.thingspeak.com/update?api_key={TS_key}"
            field = "field7"
            url = f"{BASE_URL}&{field}={HUMIDEX}"
            response = requests.get(url)

        elif measure == 'particulate':
            self.lastP.append(measure_to_check)
            AIQ = self.AIQ()
            self.hourly_average_P = self.average(self.lastP, self.hourly_average_P)
            # send AIQ to thingSpeak
            BASE_URL = f"https://api.thingspeak.com/update?api_key={TS_key}"
            field = "field8"
            url = f"{BASE_URL}&{field}={AIQ}"
            response = requests.get(url)

        elif measure == 'motion':
            self.lastM.append(measure_to_check)
            self.hourly_average_M = self.average(self.lastM, self.hourly_average_M)

    # to use
    def Breakpoints(self, C_P):
        print(C_P)
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

    def AIQ(self):
        # C_P is the rounded concentration of pollutant p
        # BP_HI is the breakpoint greater than or equal to C_P
        # BP_LO is the breakpoint less than or equal to C_P
        # I_HI = the AQI value corresponding to BP_HI
        # I_LO = the AQI value corresponding to BP_LO
        BP_LO, BP_HI, I_LO, I_HI, category = self.Breakpoints(self.lastP[-1])
        AIQ = int((I_HI - I_LO) / (BP_HI - BP_LO) * (self.lastP[-1] - BP_LO) + I_LO)
        return AIQ  # , category

    def HUMIDEX(self):
        # T is the air temperature
        # RH is the relative humidity
        H = self.lastT[-1] + (0.5555 * (0.06 * self.lastH[-1] / 100 * 10 ** (0.03 * self.lastT[-1]) - 10))
        if H < 27:
            category = "Comfort"
        elif 27 <= H < 30:
            category = "Cautela"
        elif 30 <= H < 40:
            category = "Estrema cautela"
        elif 40 <= H < 55:
            category = "Pericolo"
        else:
            category = "Estremo pericolo"
        return H  # , category

    def average(self, list, average):

        if len(list) > 3600 / self.timegap:  # 3600/30=120
            tmp_list = list[1::]
        else:
            tmp_list = list
        average = np.mean(np.array(tmp_list))
        return average


if __name__ == '__main__':

    with open("settings.json", 'r') as f:
        settings = json.load(f)

    # vedere se si prendono da CATALOG le info qua sotto

    baseTopic = settings["baseTopic"]
    broker = settings["broker"]
    port = settings["port"]
    clientID = "StatisticAnalyzer"

    analyzer = StatisticAnalyzer(baseTopic, broker, port, clientID)

    with open("./Database/Sensors.json", "r") as f:
        all_sensors = json.load(f)

    topic = '/'.join([baseTopic, '#'])
    analyzer.start(topic)

    while True:
        pass
