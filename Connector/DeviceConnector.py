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

import requests
import json
import cherrypy


class DeviceConnector:

    def __init__(self):
        with open('service_catalog_info.json', 'r') as f:
            config = json.load(f)

        self.ServiceCatalog_host = config["service_host"]
        self.ServiceCatalog_port = config["service_port"]
        self.request_RC_command = config["RC_request"]
        self.sensor_registration_command = config["DC_sensor_registration"]
        self.device_registration_command = config["DC_device_registration"]
        self.RC_host = ""
        self.RC_port = ""
        self.RC_name = ""
        # devices and reources direttamente legati a questo Device Connector. Per ogni rasp che si ha, si crea un nuovo
        # Device Connector --> ogni Device Connector fa riferimento solo ai sensori/attuatori collegati ad un certo rasp
        self.sensors_file = "sensors.json"
        self.devices_file = "devices.json"

    def request_RC(self, RC_name):
        command = self.request_RC_command
        url = self.ServiceCatalog_host + ':' + self.ServiceCatalog_port + '/' + command
        payload = {"RC_name": RC_name}
        r = requests.get(url=url, data=payload)
        RC_info = r.json()
        self.RC_host = RC_info["host"]
        self.RC_port = RC_info["port"]
        # self.RC_name = RC_info["catalog_name"]

    def registration(self):  # devices and resources registration inside the RESOURCE CATALOG -> called in a loop
        # per ora mi vengono solo in mente sensori/attuatori che sono gestiti da un Device Connector
        # SENSORS REGISTRATION
        #TODO la registrazione nel database andrebbe fatta da zero ogni volta così si tolgono anche i sensori che son stati rimossi
        command = self.sensor_registration_command
        with open(self.sensors_file, 'r') as f:
            sensors_list = json.load(f)

        for sensor in sensors_list:
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


class ServicesComponent:

    # MQTT COMMUNICATION
    # chiamiamo la funzione di publish di ogni singolo sensore associato a questo device connector (quindi nel file
    # "sensors.json")

    # REST COMMUNICATION
    exposed = True

    def GET(self, *uri, **params):  # come passiamo l'id?? --> vedere con Andre
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

    # DEVICE CONNECTOR INFO

    with open('device_connector_info.json', 'r') as f:
        d_config = json.load(f)

    port = d_config["connector_port"]

    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on': True
        }
    }

    cherrypy.tree.mount(ServicesComponent(), '/DC', conf)
    cherrypy.config.update({'server.socket_port': port})
    cherrypy.config.update(conf)

    cherrypy.engine.start()

    while True:
        raspberry.registration()
        time.sleep(30*60) # ogni 30 min?

    cherrypy.engine.block()


    r = requests.get(url)
