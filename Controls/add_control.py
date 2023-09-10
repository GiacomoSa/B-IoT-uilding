import json
if __name__=="__main__":
    buildings = json.load(open("../Database/Buildings.json", 'r'))
    sensors = json.load(open("../Database/Sensors.json", 'r'))
    sensors = sensors[0]['sensors']
    controls = json.load(open("./actuators.json", 'r'))
    buildings_id_list = [building['building_id'] for building in buildings]
    id = buildings_id_list[0]
    rooms = [building['rooms'] for building in buildings if building['building_id'] == id]
    room = rooms[0]
    possible_measures_to_check = ['temperature', 'particulate', 'motion']
    measure_to_check = possible_measures_to_check[0]

    found = False
    for control in controls:
        if control['building_id'] == id and control['room_id'] == room and control['measure_to_check']== measure_to_check:
            found = True
            break
    if found:
        raise Exception("Control already present in our system")
    else:
        to_append = {
        "control_id": str(int(controls[-1]['control_id']) + 1),
        "building_id": id,
        "room_id": room,
        "measure_to_check": measure_to_check}
    dbg = True