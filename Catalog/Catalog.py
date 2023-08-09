"""
dentro al Catalog ci saranno:

- DataBase
    - readFromJSON

- Building
    - getBuildingID
    - getRooms
    - getDevices
    - addRoom
    - addUser
    -

- Room
    - getRoomID
    - getDevices
    - addDevice

- Device (sensor)
    - getDeviceID
    - getMeasureType

- User
    - getUserID
    - getUserBuilding
    - getDevices

- SuperUser (eredita da User)(potrebbe anche solo essere un flag dentro User)

"""


class DatabaseManager():

    def __init__(self, file_path):
        self.file_path = file_path
        self.building_list = []
        self.devices_list = []
        self.users_list = []


    def load(self):


class Building():

    def __init__(self, buildingID, building_type, building_address):
        self.buildingID:str = buildingID
        self.building_type:str = building_type # ???
        self.building_address = building_address
        self.rooms = [] # list of roomID
        self.users = []  # users with access to the building (sensors, actuators ecc) -- list of userID

    """
    Get attributes section
    """

    def getAllInfo(self):  # questa può essere sostituita con vars(Building) dentro al CatalogManager.py
        return self.__dict__  # __dict__ usato + per memoria, vedere sennò come si usa __slots__: https://stackoverflow.com/questions/19907442/explain-dict-attribute

    def getBuildingID(self):
        return self.buildingID

    def getBuildingType(self):
        return self.buildingType

    def getRooms(self):
        return self.rooms

    def getUser(self):
        return self.users

    """
    Add attributes section
    """

    def addRoom(self, roomID):
        self.rooms.append(roomID)

    def addUser(self, userID):
        self.rooms.append(userID)


class Room():

    def __init__(self, roomID):
        self.roomID = roomID
        self.devices = [] # list of devicesID

    def getDevices(self):
        return self.devices

    def addDevice(self, device):
        self.devices.append(device)


class Device():

    def __init__(self, deviceID, measure_type, buildingID, roomID):
        self.deviceID = deviceID
        self.measure_type = measure_type
        self.buildingID = buildingID
        self.roomID = roomID
        self.device_topic = "/".join((self.buildingID, self.roomID, self.deviceID))


class User():

    def __init__(self):
        self.buildings = []
        self.isSuper = False # if superUser or not

    def getDevices(self):
        dev_list = []

        for b in self.buildings:
            for r in b.rooms:
                tmp = r.devices
                dev_list.append(*tmp)

        return dev_list




