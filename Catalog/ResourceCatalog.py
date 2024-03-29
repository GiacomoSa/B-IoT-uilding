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
import random

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

    def remainingBuildings(self, username):
        with open("../Database/Users.json", "r") as f:
            user_list = json.load(f)

        for user in user_list:
            if user["username"] == username:
                buildings_list = user["owned_buildings"] + user["observed_buildings"]
                break

        remaining_buildings = [b["building_id"] for b in self.buildings]

        el_to_delete = []
        for bb in remaining_buildings:
            for bbb in buildings_list:
                if bb == bbb:
                    el_to_delete.append(bb)

        l = copy.copy(len(el_to_delete))
        for i in range(l):
            remaining_buildings.remove(el_to_delete[i])

        for idx, ele in enumerate(remaining_buildings):
            for building in self.buildings:
                if ele == building["building_id"]:
                    name = building["building_name"]
                    remaining_buildings[idx] = f"{name}:{ele}"

        return remaining_buildings

    exposed = True

    def GET(self, *uri, **params):

        command = str(uri)[2:-3]

        if command == "remainingBuildings":

            username = params["username"]
            rem_buildings = self.remainingBuildings(username)
            return json.dumps(rem_buildings)

        elif command == "ofUser":  # w...../building/ofUser?username=userid

            username = params["username"]

            with open("../Database/Users.json") as f:
                list_users = json.load(f)

            for user in list_users:
                if username == user["username"]:
                    my_buildings = user["owned_buildings"]
                    obs_buildings = user["observed_buildings"]
                    break

            owned_building_names = []
            for building_id in my_buildings:
                for building in self.buildings:
                    if building_id == building["building_id"]:  # ["Museo:1", "Casa:2", "Scuola:3"]
                        name = building["building_name"]
                        owned_building_names.append(f"{name}:{building_id}")

            observed_building_names = []
            for building_id in obs_buildings:
                for building in self.buildings:
                    if building_id == building["building_id"]:  # ["Museo:1", "Casa:2", "Scuola:3"]
                        name = building["building_name"]
                        observed_building_names.append(f"{name}:{building_id}")

            all_buildings = {
                "owned_buildings": owned_building_names,
                "observed_buildings": observed_building_names
            }


            return json.dumps(all_buildings)

        elif command == "getTSlink":

            building_id = params["building_id"]
            room_id = params["room_id"]

            TS_link = ""
            for building in self.buildings:
                if building["building_id"] == building_id:
                    TS_link_list = building["TS_links"]
                    TS_link = TS_link_list[room_id]

            return TS_link

        else:

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
        new_building = json.loads(cherrypy.request.body.read())
        building_id = str(int(self.buildings[-1]["building_id"]) + 1)
        new_building["building_id"] = building_id

        self.insertBuilding(new_building)

        username = params["username"] # AGGIUNGERE USERNAME SULL'APPPPP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        type = params["type"]

        with open('resource_catalog_info.json', 'r') as f:
            r_config = json.load(f)
            host = r_config["resource_host"]
            port = int(r_config["resource_port"])

        user_url = f"{host}:{port}/user/building?type={type}"
        payload = {
            "username": username,
            "building_id": building_id,
        }
        requests.put(user_url, json.dumps(payload))

        return "Building addedd succesfully"

    def PUT(self, *uri, **params):

        """
        modify a building info
        """

        command = str(uri)[2:-3]

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


class CatalogUSER:  # mounted on '/user'

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

    def deleteBuildingFromUser(self, username, building):
        for user in self.users:
            if username == user["username"]:
                if building in user["owned_buildings"]:
                    user["owned_buildings"].remove(building)
                elif building in user["observed_buildings"]:
                    user["observed_buildings"].remove(building)
                break
        with open(self.userdb_file, "w") as file:
            json.dump(self.users, file, indent=4)

    def addBuildingToUser(self, username, building, type):

        if type == "owned":
            for user in self.users:
                if username == user["username"]:
                    user["owned_buildings"].append(building)
                    break
        elif type == "observed":
            for user in self.users:
                if username == user["username"]:
                    user["observed_buildings"].append(building)
                    break
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
        if str(uri)[2:-3] == "building":

            updating_values = json.loads(cherrypy.request.body.read())

            username = updating_values["username"]
            building = updating_values["building_id"]
            type = params["type"]

            self.addBuildingToUser(username, building, type)

        else:
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

        if str(uri)[2:-3] == "building":

            username = params["username"]
            building = params["building_id"]

            self.deleteBuildingFromUser(username, building)


        else:

            try:
                id = params["id"]

            except:
                raise cherrypy.HTTPError(400, 'Bad request')

            found = False
            for idx, user in enumerate(self.users):
                if user["username"] == id:
                    self.deleteUser(idx)
                    break

            if not found:
                raise cherrypy.HTTPError(400, f'Bad request - User {id} not found')


class CatalogDEVICE:  # mounted on '/devices'

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


class CatalogSENSOR:  # mounted on '/sensors'

    def __init__(self, sensordb_file):
        self.sensordb_file = sensordb_file
        with open(sensordb_file, 'r') as file:
            self.sensors: list = json.load(file)

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

        if command == "missing":

            building_id = params["building_id"]
            room_id = params["room_id"]
            catalog_id = params["catalog_id"]

            default_measures = ["temperature", "humidity", "motion", "particulate"]

            for s in self.sensors:
                if s["catalog_id"] == catalog_id:
                    tutti_sensori = copy.deepcopy(s["sensors"])

            for sensor in tutti_sensori:
                if sensor["building_id"] == building_id and sensor["room_id"] == room_id:
                    default_measures.remove(sensor["measure"])

            if len(default_measures) == 0:
                raise cherrypy.HTTPError(400, "Bad request")
            else:
                return json.dumps(default_measures)

        else:

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
        add a new sensor
        """

        new_sensor = json.loads(cherrypy.request.body.read())
        measure = new_sensor["sensor_measure"]
        building_id = new_sensor["building_id"]
        room_id = new_sensor["room_id"]
        catalog_id = new_sensor["catalog_id"]

        for s in self.sensors:
            if s["catalog_id"] == catalog_id:
                tutti_sensori = s["sensors"]

        new_id = str(int(tutti_sensori[-1]["sensor_id"]) + 1)

        path = os.path.dirname(__file__)
        measure_units = json.load(open(os.path.join(path, "measure_units.json")))

        json_obj = {
            "sensor_id": new_id,
            "building_id": building_id,
            "room_id": room_id,
            "measure": measure,
            "measure_unit": measure_units[measure]
        }

        # add to database

        tutti_sensori.append(json_obj)
        with open(self.sensordb_file, "w") as file:
            json.dump(self.sensors, file, indent=4)

        # add to local catalog
        with open('resource_catalog_info.json', 'r') as f:
            r_config = json.load(f)
        host = r_config["resource_host"]
        port = int(r_config["resource_port"])
        catalog_name = r_config["catalog_name"]
        url = f"{host}:{port}/resource?id=all"
        r = requests.get(url)

        all_resources = json.loads(r.text)
        for resource in all_resources:
            if resource["catalog_id"] == catalog_name:
                connector_info = copy.deepcopy(resource)
                break
        connector_host = connector_info["host"]
        connector_port = connector_info["port"]
        url2 = f"{connector_host}:{connector_port}/Data?catalog_id={catalog_name}"

        r = requests.post(url=url2, data=json.dumps(json_obj))

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


class CatalogRESOURCES:  # mounted on /resource

    def __init__(self, resourcedb_file):
        self.resourcedb_file = resourcedb_file
        with open(self.resourcedb_file, 'r') as file:
            self.resources = json.load(file)

    # ----- DEVICE -----
    def insertResource(self, device_json):
        found = False
        for res in self.resources:
            if res["catalog_id"] == device_json["catalog_id"]:
                found = True
                break
        if not found:
            self.resources.append(device_json)
            with open(self.resourcedb_file, "w") as file:
                json.dump(self.resources, file, indent=4)

    def updateResource(self, updated_device, idx):
        self.resources[idx] = copy.deepcopy(updated_device)
        with open(self.resourcedb_file, "w") as file:
            json.dump(self.resources, file, indent=4)

    def deleteResource(self, idx):
        self.resources.pop(idx)
        with open(self.resourcedb_file, "w") as file:
            json.dump(self.resources, file, indent=4)

    exposed = True

    def GET(self, *uri, **params):

        try:
            id = params["id"]

        except:
            raise cherrypy.HTTPError(400, 'Bad request')

        if id == "all":
            # ritorniamo tutti
            return json.dumps(self.resources)

        else:
            found = False
            for b in self.resources:
                if b["resource_id"] == id:
                    found = True
                    return json.dumps(b)

            if not found:
                raise cherrypy.HTTPError(400, f'Bad request - Resource {id} not found')

    def POST(self, *uri, **params):

        """
        add a new resource
        """
        new_resource = params
        #new_resource = json.loads(cherrypy.request.body.read())
        self.insertResource(new_resource)

        return  # ???

    def PUT(self, *uri, **params):

        """
        modify a resource info
        """

        try:
            id = params["id"]
        except:
            raise cherrypy.HTTPError(400, 'Bad request')

        found = False
        for idx, resource in enumerate(self.resources):
            if resource['resource_id'] == id:
                found = True

                updated_resource = json.loads(cherrypy.request.body.read())
                self.updateResource(updated_resource, idx)
                break

        if not found:
            raise cherrypy.HTTPError(400, f'Bad request - Device {id} not found')

    def DELETE(self, *uri, **params):

        try:
            id = params["id"]

        except:
            raise cherrypy.HTTPError(400, 'Bad request')

        found = False
        for idx, resource in enumerate(self.resources):
            if resource["resource_id"] == id:
                self.deleteResource(idx)
                break

        if not found:
            raise cherrypy.HTTPError(400, f'Bad request - Resource {id} not found')


class RegistrationManager:  # mounted on /registration

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

            for connector in connector_list:  # questo connector è un dizionario con primo elemento l'id del catalog, secondo elemento lista di sensori
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
    app_host = r_config["app_host"]

    buildings_db = "../Database/Buildings.json"
    users_db = "../Database/Users.json"
    devices_db = "../Database/Devices.json"
    sensors_db = "../Database/Sensors.json"
    resources_db = "../Database/Resources.json"

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
    cherrypy.tree.mount(CatalogRESOURCES(resources_db), '/resource', conf)

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
        "catalog_name": catalog_name,
        "app_host": app_host
    }

    while True:
        service_url = service_host + ':' + service_port + '/' + service_endpoint
        r = requests.post(service_url, data=registration_info)
        print(r.text)
        time.sleep(300)

    cherrypy.engine.block()
