"""
Qua c'è la parte REST del Resource Catalog
Stesse classi di Catalog.py ma con funzioni REST (GET, POST, PUT, DELETE)

Una classe x gestire i Sensori (GET, POST, PUT, DELETE)     | montata su /Sensor    } SOLO SUPERUSER!!
Una classe x gestire gli utenti (GET, POST, PUT, DELETE)    | montata su /User
Una classe x gestire i Building (GET, POST, PUT, DELETE)    | montata su /Building  } SOLO
Una classe x gestire i Devices (GET, POST, PUT, DELETE)     | montata su /Device    } SUPERUSERS!!
    - info del Catalog stesso (GET) ???

CatalogManager.py --> Catalog.py
"""

import json
import cherrypy
# from Catalog import *
import copy
import os
import requests
import time

# TODO l'id con cui aggiungiamo elementi in una POST lo generiamo noi??

class CatalogBUILDING:  # mounted on '/building'

    def __init__(self, buildingdb_file):
        self.buildingdb_file = buildingdb_file
        with open(buildingdb_file, 'r') as file:
            self.buildings = json.load(file)

    # ----- BUILDING -----
    def insertBuilding(self, building_json):
        self.buildings.append(building_json)
        with open(self.buildingdb_file, "w") as file:
            json.dump(self.buildings, file, indent=4)

    def updateBuilding(self, updated_building, idx):
        self.buildings[idx] = copy.deepcopy(updated_building)
        with open(self.buildingdb_file, "w") as file:
            json.dump(self.buildings, file, indent=4)

    def deleteBuilding(self, idx):
        self.buildings.pop(idx)
        with open(self.buildingdb_file, "w") as file:
            json.dump(self.buildings, file, indent=4)

    exposed = True

    def GET(self, *uri, **params):

        command = str(uri)[2:-3]

        try:
            id = params["id"]

        except:
            raise cherrypy.HTTPError(400, 'Bad request')

        if id == "all":
            # ritorniamo tutti
            return json.dumps(self.buildings)

        else:
            found = False
            for b in self.buildings:
                if b["building_id"] == id:
                    found = True
                    return json.dumps(b)

            if not found:
                raise cherrypy.HTTPError(400, f'Bad request - Building {id} not found')

    def POST(self, *uri, **params):

        """
        add a new building
        """
        command = str(uri)[2:-3]

        if command == "building":
            new_building = json.loads(cherrypy.request.body.read())
            self.insertBuilding(new_building)

        return  # ???

    def PUT(self, *uri, **params):

        """
        modify a building info
        """

        command = str(uri)[2:-3]

        if command == "building":

            try:
                id = params["id"]
            except:
                raise cherrypy.HTTPError(400, 'Bad request')

            found = False
            for idx, building in enumerate(self.buildings):
                if building['building_id'] == id:
                    found = True

                    updated_building = json.loads(cherrypy.request.body.read())
                    self.updateBuilding(updated_building, idx)
                    break

            if not found:
                raise cherrypy.HTTPError(400, f'Bad request - Building {id} not found')

    def DELETE(self, *uri, **params):

        command = str(uri)[2:-3]

        if command == 'building':

            try:
                id = params["id"]

            except:
                raise cherrypy.HTTPError(400, 'Bad request')

            found = False
            for idx, building in enumerate(self.buildings):
                if building["building_id"] == id:
                    self.deleteBuilding(idx)
                    break

            if not found:
                raise cherrypy.HTTPError(400, f'Bad request - Building {id} not found')


class CatalogUSER: # mounted on '/Users'

    def __init__(self, userdb_file):
        self.userdb_file = userdb_file
        with open(userdb_file, 'r') as file:
            self.users = json.load(file)

    # ----- USER -----
    def insertUser(self, user_json):
        self.users.append(user_json)
        with open(self.userdb_file, "w") as file:
            json.dump(self.users, file, indent=4)

    def updateUser(self, updated_user, idx):
        self.users[idx] = copy.deepcopy(updated_user)
        with open(self.userdb_file, "w") as file:
            json.dump(self.users, file, indent=4)

    def deleteUser(self, idx):
        self.users.pop(idx)
        with open(self.userdb_file, "w") as file:
            json.dump(self.users, file, indent=4)

    exposed = True

    def GET(self, *uri, **params):

        try:
            id = params["id"]

        except:
            raise cherrypy.HTTPError(400, 'Bad request')

        if id == "all":
            # ritorniamo tutti
            return json.dumps(self.users)

        else:
            found = False
            for b in self.users:
                if b["user_id"] == id:
                    found = True
                    return json.dumps(b)

            if not found:
                raise cherrypy.HTTPError(400, f'Bad request - User {id} not found')

    def POST(self, *uri, **params):

        """
        add a new user
        """

        new_user = json.loads(cherrypy.request.body.read())

        found = False
        for us in self.users:
            if new_user["username"] == us["username"]:
                found = True
                break

        if found:
            raise cherrypy.HTTPError(400, f'User {new_user["username"]} already existing')  # user already existing
        else:
            self.insertUser(new_user)


    def PUT(self, *uri, **params):

        """
        modify a building info
        """

        try:
            id = params["id"]
        except:
            raise cherrypy.HTTPError(400, 'Bad request')

        found = False
        for idx, user in enumerate(self.users):
            if user['user_id'] == id:
                found = True

                updated_user = json.loads(cherrypy.request.body.read())
                self.updateUser(updated_user, idx)
                break

        if not found:
            raise cherrypy.HTTPError(400, f'Bad request - User {id} not found')

    def DELETE(self, *uri, **params):

        try:
            id = params["id"]

        except:
            raise cherrypy.HTTPError(400, 'Bad request')

        found = False
        for idx, user in enumerate(self.users):
            if user["user_id"] == id:
                self.deleteUser(idx)
                break

        if not found:
            raise cherrypy.HTTPError(400, f'Bad request - User {id} not found')


class CatalogDEVICE: # mounted on '/Users'

    def __init__(self, devicedb_file):
        self.devicedb_file = devicedb_file
        with open(devicedb_file, 'r') as file:
            self.devices = json.load(file)

    # ----- DEVICE -----
    def insertDevice(self, device_json):
        self.devices.append(device_json)
        with open(self.devicedb_file, "w") as file:
            json.dump(self.devices, file, indent=4)

    def updateDevice(self, updated_device, idx):
        self.devices[idx] = copy.deepcopy(updated_device)
        with open(self.devicedb_file, "w") as file:
            json.dump(self.devices, file, indent=4)

    def deleteDevice(self, idx):
        self.devices.pop(idx)
        with open(self.devicedb_file, "w") as file:
            json.dump(self.devices, file, indent=4)

    exposed = True

    def GET(self, *uri, **params):

        try:
            id = params["id"]

        except:
            raise cherrypy.HTTPError(400, 'Bad request')

        if id == "all":
            # ritorniamo tutti
            return json.dumps(self.devices)

        else:
            found = False
            for b in self.devices:
                if b["device_id"] == id:
                    found = True
                    return json.dumps(b)

            if not found:
                raise cherrypy.HTTPError(400, f'Bad request - Device {id} not found')

    def POST(self, *uri, **params):

        """
        add a new user
        """

        new_device = json.loads(cherrypy.request.body.read())
        self.insertDevice(new_device)

        return  # ???

    def PUT(self, *uri, **params):

        """
        modify a building info
        """

        try:
            id = params["id"]
        except:
            raise cherrypy.HTTPError(400, 'Bad request')

        found = False
        for idx, device in enumerate(self.devices):
            if device['device_id'] == id:
                found = True

                updated_device = json.loads(cherrypy.request.body.read())
                self.updateDevice(updated_device, idx)
                break

        if not found:
            raise cherrypy.HTTPError(400, f'Bad request - Device {id} not found')

    def DELETE(self, *uri, **params):

        try:
            id = params["id"]

        except:
            raise cherrypy.HTTPError(400, 'Bad request')

        found = False
        for idx, device in enumerate(self.devices):
            if device["device_id"] == id:
                self.deleteDevice(idx)
                break

        if not found:
            raise cherrypy.HTTPError(400, f'Bad request - Device {id} not found')


class CatalogSENSOR: # mounted on '/sensors'

    def __init__(self, sensordb_file):
        self.sensordb_file = sensordb_file
        with open(sensordb_file, 'r') as file:
            self.sensors = json.load(file)

    # ----- SENSOR -----
    def insertSensor(self, sensor_json):
        self.sensors.append(sensor_json)
        with open(self.sensordb_file, "w") as file:
            json.dump(self.sensors, file, indent=4)

    def updateSensor(self, updated_sensor, idx):
        self.sensors[idx] = copy.deepcopy(updated_sensor)
        with open(self.sensordb_file, "w") as file:
            json.dump(self.sensors, file, indent=4)

    def deleteSensor(self, idx):
        self.sensors.pop(idx)
        with open(self.sensordb_file, "w") as file:
            json.dump(self.sensors, file, indent=4)

    def returnTopicByID(self, sensor_id):
        for sensor in self.sensors:
            if sensor["sensor_id"] == sensor_id:
                return json.dum

    exposed = True

    def GET(self, *uri, **params):

        command = str(uri)[2:-3]

        try:
            id = params["id"]

        except:
            raise cherrypy.HTTPError(400, 'Bad request')

        if id == "all":
            # ritorniamo tutti
            return json.dumps(self.sensors)

        else:
            found = False
            for b in self.sensors:
                if b["user_id"] == id:
                    found = True
                    return json.dumps(b)

            if not found:
                raise cherrypy.HTTPError(400, f'Bad request - Sensor {id} not found')

    def POST(self, *uri, **params):

        """
        add a new user
        """

        new_sensor = json.loads(cherrypy.request.body.read())
        new_sensor_id = new_sensor["sensor_id"]
        for sensor in self.sensors:
            found = False
            if new_sensor_id == sensor["sensor_id"]:
                found = True
                break
            if not found:
                self.insertSensor(new_sensor)

        return  # ???

    def PUT(self, *uri, **params):

        """
        modify a building info
        """

        try:
            id = params["id"]
        except:
            raise cherrypy.HTTPError(400, 'Bad request')

        found = False
        for idx, sensor in enumerate(self.sensors):
            if sensor['sensor_id'] == id:
                found = True

                updated_sensor = json.loads(cherrypy.request.body.read())
                self.updateSensor(updated_sensor, idx)
                break

        if not found:
            raise cherrypy.HTTPError(400, f'Bad request - Sensor {id} not found')

    def DELETE(self, *uri, **params):

        try:
            id = params["id"]

        except:
            raise cherrypy.HTTPError(400, 'Bad request')

        found = False
        for idx, sensor in enumerate(self.sensors):
            if sensor["sensor_id"] == id:
                self.deleteSensor(idx)
                break

        if not found:
            raise cherrypy.HTTPError(400, f'Bad request - Sensor {id} not found')


class RegistrationManager:

    def __init__(self):
        self.sensors_db = "../Database/Sensors.json"
        self.devices_db = "../Database/Devices.json"

    exposed = True

    def POST(self, *uri, **params):

        command = str(uri)[2:-3]

        # SENSOR REGISTRATION
        if command == "sensor":
            RC_name = params["RC_name"]
            ele = params['ele']

            with open(self.sensors_db, 'r') as f:
                connector_list = json.load(f)

            found = False

            for connector in connector_list: #questo connector è un dizionario con primo elemento l'id del catalog, secondo elemento lista di sensori
                if RC_name == connector['catalog_id']:
                    sensors_list = connector['sensors']
                    found = True
                    break

            if found:
                sensors_list.append(json.loads(ele))

            with open(self.sensors_db, 'w') as f:
                json.dump(connector_list, f)
        # DEVICE REGISTRATION

    def DELETE(self, *uri, **params):

        command = str(uri)[2:-3]

        if command == "allsensors":
            RC_name = params["RC_name"]
            with open(self.sensors_db, 'r') as f:
                connector_list = json.load(f)

            found = False

            for connector in connector_list:  # questo connector è un dizionario con primo elemento l'id del catalog, secondo elemento lista di sensori
                if RC_name == connector['catalog_id']:
                    connector['sensors'] = []
                    found = True
                    break

            with open(self.sensors_db, 'w') as f:
                json.dump(connector_list, f)


if __name__ == '__main__':

    # RESOURCE CATALOG INFO
    with open('resource_catalog_info.json', 'r') as f:
        r_config = json.load(f)
    host = r_config["resource_host"]
    port = int(r_config["resource_port"])
    catalog_name = r_config["catalog_name"]

    buildings_db = "../Database/Buildings.json"
    users_db = "../Database/Users.json"
    devices_db = "../Database/Devices.json"
    sensors_db = "../Database/Sensors.json"
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        }
    }
    cherrypy.tree.mount(CatalogUSER(users_db), '/user', conf)
    cherrypy.tree.mount(CatalogBUILDING(buildings_db), '/building', conf)
    cherrypy.tree.mount(CatalogDEVICE(devices_db), '/device', conf)
    cherrypy.tree.mount(CatalogSENSOR(sensors_db), '/sensor', conf)
    cherrypy.tree.mount(RegistrationManager(), '/registration', conf)

    cherrypy.config.update({'server.socket_port': port})
    cherrypy.config.update(conf)

    cherrypy.engine.start()

    # SERVICE CATALOG INFO
    with open('service_catalog_info.json', 'r') as f:
        s_config = json.load(f)

    service_host = s_config["service_host"]
    service_port = s_config["service_port"]
    service_endpoint = s_config["RC_registration"]

    # RESOURCE CATALOG REGISTRATION PROCESS
    registration_info = {
        "host": host,
        "port": port,
        "catalog_name": catalog_name
    }

    while True:
        service_url = service_host + ':' + service_port + '/' + service_endpoint
        r = requests.post(service_url, data=registration_info)
        print(r.text)
        time.sleep(300)

    cherrypy.engine.block()
