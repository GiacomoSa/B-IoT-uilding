"""
Il service catalog deve mostrare tutti i servizi IT disponibili, HW, SW e opzioni di supporto

Il nostro service catalog deve avere:
    - informazioni sul broker
    - informazioni di cosa è possibile fare con le risorse (
        . building: avere info di tutte, di una, aggiungerne una, modificarne una, cancellarne una
        . devices: avere info di tutti, di uno, aggiungerne uno, modificarne uno, cancellarne uno
        . sensors: avere info di tutti, di uno, aggiungerne uno, modificarne uno, cancellarne uno
        . users: avere info di tutti, di uno, aggiungerne uno, modificarne uno, cancellarne uno
        )
    - quali sono le funzioni di devices (attuatori) disponibili
    - altri??

"""

import json
import os
from os.path import abspath
import cherrypy


# ------ HARDWARE ------
# !!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!
# FORSE VANNO TOLTE LE FUNZIONI CON LE INFO!!!

class SensorsInfo: # mounted on /info/sensors

    def __init__(self):
        self.html_file = './public/Info/sensor_func.html'

    exposed = True

    def GET(self, *uri, **params):

        return open(self.html_file)


class DevicesInfo:

    def __init__(self):
        self.html_file = './public/Info/device_func.html'

    exposed = True

    def GET(self, *uri, **params):

        return open(self.html_file)


class BuildingsInfo:

    def __init__(self):
        self.html_file = './public/Info/building_func.html'

    exposed = True

    def GET(self, *uri, **params):
        return open(self.html_file)


class UsersInfo:

    def __init__(self):
        self.html_file = './public/Info/user_func.html'

    exposed = True

    def GET(self, *uri, **params):
        return open(self.html_file)

#TODO mettere anche le funzioni degli attuatori
#TODO mettere info sul broker


# RC REGISTRATION PROCESS

class RCManager: # cambiare nome in RCManager ????

    def __init__(self):
        self.registered_rcs_db = '../Database/Registered RCs.json'

    exposed = True

    def GET(self, *uri, **params):

        command = str(uri)[2:-3]

        if command == "getRC":
            try:
                RC_name = params["RC_name"]
                with open(self.registered_rcs_db, 'r') as f:
                    registered_rcs = json.load(f)

                for rc in registered_rcs:
                    if rc["catalog_name"] == RC_name:
                        return json.dumps(rc)
            except:
                raise cherrypy.HTTPError(400, 'Cannot find Resource Catalog')

        elif command == "getAllRCs":
            try:
                with open(self.registered_rcs_db, 'r') as f:
                    registered_rcs = json.load(f)

                return json.dumps(registered_rcs)
            except:
                raise cherrypy.HTTPError(400, 'Bad Request')

        else:
            raise cherrypy.HTTPError(400, 'Bad Request')


    def POST(self, *uri, **params):

        command = str(uri)[2:-3]

        if command == "registration":
            resource_info = params
            name = resource_info["catalog_name"]

            try:
                with open(self.registered_rcs_db, 'r') as f:
                    registered_rcs: list = json.load(f)

                found = False
                for rc in registered_rcs:
                    if rc["catalog_name"] == resource_info["catalog_name"]: # il nome del RC è una cosa univoca!!
                        found = True
                        if rc["host"] != resource_info["host"]:
                            rc["host"] = resource_info["host"]
                        if rc["port"] != resource_info["port"]:
                            rc["port"] = resource_info["port"]
                        break
                if not found:
                    registered_rcs.append(resource_info)
                with open(self.registered_rcs_db, 'w') as f:
                    json.dump(registered_rcs, f)
            except:

                return f"Failed Registering {name}"
            else:
                return f"{name} Catalog registered successfully"
        else:
            raise cherrypy.HTTPError(400, 'Bad request')


if __name__ == '__main__':

    with open('service_catalog_info.json', 'r') as f:
        config = json.load(f)

    port = int(config["service_port"])

    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/info': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'public'  # staticdir needs an absolute path
        }
    }
    cherrypy.tree.mount(SensorsInfo(), '/info/sensors', conf)
    cherrypy.tree.mount(DevicesInfo(), '/info/devices', conf)
    cherrypy.tree.mount(BuildingsInfo(), '/info/buildings', conf)
    cherrypy.tree.mount(UsersInfo(), '/info/users', conf)
    cherrypy.tree.mount(RCManager(), '/RC', conf)

    cherrypy.config.update({'server.socket_port': port})
    cherrypy.config.update(conf)

    cherrypy.engine.start()
    cherrypy.engine.block()

