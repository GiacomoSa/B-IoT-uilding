"""
Schema device connector a slide 20 pacco 12. Supponiamo che dall'esterno chiedono la temperatura, x esempio tramite rest.
Tutto ciò che l'esterno deve sapere è il device id e il rest endpoint e basta (quindi nessuna info di come il device 1
comunica). Tutto il resto viene gestito dal connector. La richiesta viene gestita dal blocco Services (sempre nello schema),
viene forwarded al Process Manager che sa che al device di id=1 corrisponde tale device agent 1 con comunicazione
bluetooth. Il device agent chiede dunque al device1 quale sia la temperature. Cosa cambia se invece vogliamo chiedere
la temperatura ad uno stesso dispositivo che usa USB? Dal punto di vista dell'app non cambia nulla, semplicemente viene
cambiato l'id nella richiesta (STESSA COSA!); la cosa cambia nel Process Manager che sa che sta volta deve usare il
Device Agent 3.
Come funziona tutto quanto insieme? SLIDE 29
Il Service Catalog è l'end point per tutti gli attori nel sistema, anche per il resource catalog. Quindi il Service
Catalog deve essere sempre up and running. Quando il Resource si accende, deve registrarsi nel Service Catalog e questo
deve essere fatto continuamente -> questo perchè il Service deve essere sempre aggiornato per dare le giuste informazioni
riguardo ai microservices disponibili.

Una volta che compare un Device Connector (SLIDE 23), questo deve registrare tutti gli IoT devices che gestisce nel
Resoource Catalog. La prima cosa che chiede al Service è: dov'è il Resource Catalog? In poche parole il DevConn chiede
al Service qual è l'endpoint del Reource in cui può registrare i metadati dei devices (DISCOVERY PROCESS).
Ora il Connector può registrare tutti i metadati nel Resource e lo fa in un loop (REGISTRATION PROCESS).
Ad un certo punto compare un'applicazione nel nostro sistema (sarebbe il service customer, SLIDE 26); supponiamo che
questa app chieda un'info specifica riguardo a un dispositivo IoT nel sistema (es. temp). La prima cosa che l'app fa
è chiedere al Service dov'è il Resource Catalog. Ora l'app conosce gli endpoints del Resuorce e gli chiede quale è il
Device Connector che integra il device da cui deve prendere l'informazione (2nd DISCOVERY PROCESS). Infine l'app contatta
il Device Connector chiedendo la temperatura di cui ha bisogno -> quindi il Device Connector seguirà tutti gli step nello
schema a SLIDE 20.
Lo schema a SLIDE 29 riassume tutti i microservizi in verità: se voglio aggiungere un nuovo microservizio che da informazioni,
allora lo userò come un resource catalog, se voglio aggiungere una sorta di applicazione, allora funzionerà come l'applicazione.


LEZ 29/11/21
"""
import time
import random
import requests
import json
import cherrypy
from sensor_temperature import Sensor as SensorTemperature

class DeviceConnector:

    def __init__(self):
        with open("../Catalog/service_catalog_info.json", 'r') as f:
            config = json.load(f)

        self.ServiceCatalog_host = config["service_host"]
        self.ServiceCatalog_port = config["service_port"]
        self.request_RC_command = config["RC_request"]
        self.sensor_registration_command = config["DC_sensor_registration"]
        self.device_registration_command = config["DC_device_registration"]
        self.sensors_delete_command = config["delete_sensors"]
        self.RC_host = ""
        self.RC_port = ""
        self.RC_name = ""
        # devices and reources direttamente legati a questo Device Connector. Per ogni rasp che si ha, si crea un nuovo
        # Device Connector --> ogni Device Connector fa riferimento solo ai sensori/attuatori collegati ad un certo rasp
        self.sensors_file = "sensors.json"
        self.devices_file = "devices.json"

    def request_RC(self, RC_name):
        command = self.request_RC_command
        url = self.ServiceCatalog_host + ':' + self.ServiceCatalog_port + '/' + command + f"?RC_name={RC_name}"
        payload = {"RC_name": RC_name}
        r = requests.get(url=url, data=payload)
        RC_info = r.json()
        self.RC_host = RC_info["host"]
        self.RC_port = RC_info["port"]
        self.RC_name = RC_info["catalog_name"]

    def registration(self):  # devices and resources registration inside the RESOURCE CATALOG -> called in a loop
        # per ora mi vengono solo in mente sensori/attuatori che sono gestiti da un Device Connector
        # SENSORS REGISTRATION
        #TODO la registrazione nel database andrebbe fatta da zero ogni volta così si tolgono anche i sensori che son stati rimossi
        command = self.sensor_registration_command
        with open(self.sensors_file, 'r') as f:
            sensors_list = json.load(f)

        delete_command = self.sensors_delete_command
        url = self.RC_host + ':' + self.RC_port + '/' + delete_command + "?RC_name=" + self.RC_name
        delete_payload = {'RC_name': self.RC_name}
        r = requests.delete(url, data=delete_payload)

        for sensor in sensors_list['sensors']:
            url = self.RC_host + ':' + self.RC_port + '/' + command

            payload = {'RC_name': self.RC_name, 'ele': json.dumps(sensor)}
            r = requests.post(url, data=payload)

        # DEVICES REGISTRATION
        command = self.device_registration_command
        with open(self.devices_file, 'r') as f:
            devices_list = json.load(f)

        for device in devices_list:
            url = self.RC_host + ':' + self.RC_port + '/' + command

            payload = {'RC_name': self.RC_name, 'ele': json.dumps(device)}
            r = requests.post(url, data=payload)


# --- SERVICES COMPONENT --- #

class ServicesComponent: # mounted on /Data

    # MQTT COMMUNICATION
    # chiamiamo la funzione di publish di ogni singolo sensore associato a questo device connector (quindi nel file
    # "sensors.json")

    # REST COMMUNICATION
    exposed = True

    def GET(self, *uri, **params):  # come passiamo l'id?? --> vedere con Andre
        command = str(uri)[2:-3]
        if command == "sensor": #params -> id, cosa misura

            data = [{
                    "sensor_id": "chiesa",
                    "value": random.gauss(25, 1),
                    "measure": "temperatura"
                },
                {
                    "sensor_id": "chiesa1",
                    "value": random.gauss(50, 5),
                    "measure": "humidity"
                },
                {
                    "sensor_id": "chiesa2",
                    "value": "off",
                    "measure": "lighting"
                },
                {
                    "sensor_id": "chiesa3",
                    "value": random.randint(0, 10),
                    "measure": "people"
                },
                {
                    "sensor_id": "chiesa4",
                    "value": random.gauss(200, 10),
                    "measure": "PM10"
                }
            ]
            return json.dumps(data)
        pass

    def POST(self, *uri, **params):  # per aggiungere sensori al device connector?
        pass

    def PUT(self, *uri, **params):  # per modificare un sensore già associato al dev connector?
        pass

    def DELETE(self, *uri, **params):  # per cancellare un sensore rimosso?
        pass


if __name__ == '__main__':
    raspberry = DeviceConnector()
    RC_name = "B(IoT)uilding"
    raspberry.request_RC(RC_name=RC_name)
    #Fa partire lo start di tutti i sensori
    #Il device connector deve far fare il .publish
    #Prima fase di requestRC. poi una fase di registration, ogni tot second fa partire il .publish dei sensori
    #OGni 50 secondi per esempio di nuovo registration. Magari si è aggiunto un nuovo sensore che è aggiunto solo al file locale
    # sensor.json ma non in quello del database, Appena c'è un nuovo sensore li stoppo tutti e poi li faccio ripartire con quello nuovo,
    # ma fino alla registration il resource non sa che esiste e quindi nessuno potrà vedere i suoi dati

    sensors = json.load(open("sensors.json"))
    temp_sens = []
    hum_sens = []
    part_sens = []
    motion_sens = []

    for sensor in sensors['sensors']:
        if sensor['measure'] == 'temperature':
            # class sensor wants buildingID,roomID,sensorID,broker,port, measure, measure_unit
            sensor = SensorTemperature(buildingID=sensor['building_id'], roomID=sensor['room_id'], sensorID=sensor['sensor_id'],
                                       measure=sensor['measure'], measure_unit=sensor['measure_unit'])
            sensor.start()
            temp_sens.append(sensor)

    # DEVICE CONNECTOR INFO

    with open('device_connector_info.json', 'r') as f:
        d_config = json.load(f)

    port = int(d_config["connector_port"])

    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on': True
        }
    }

    cherrypy.tree.mount(ServicesComponent(), '/Data', conf)
    cherrypy.config.update({'server.socket_port': port})
    cherrypy.config.update(conf)

    cherrypy.engine.start()

    start_send = time.time()
    start_reg = time.time()
    while True:
        #if time.time() - start_send > 1:
        #    pass
            #for sensor in temp_sens:
            #    sensor.sendData() #Publish
            #    start_send = time.time()
        if time.time() - start_reg > 1:
            #Prima della registration il file coi sensor del database va svuotato
            raspberry.registration()
            start_reg = time.time()


    # quando faremo la comunicazione dall'app con Andre, spostare questa parte (in cui si monta il tree di cherrypy...)
    # prima del while True sopra



    cherrypy.engine.block()



