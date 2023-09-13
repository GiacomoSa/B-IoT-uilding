import json
if __name__=="__main__":
    buildings = json.load(open("../Database/Buildings.json", 'r'))
    sensors = json.load(open("../Database/Sensors.json", 'r'))
    sensors = sensors[0]['sensors']
    controls = json.load(open("./actuators.json", 'r'))
    buildings_id_list = [building['building_id'] for building in buildings]
    id = input(f"For which building do you wish to add a control? Choose among these: {buildings_id_list}\n>>")
    rooms = [building['rooms'] for building in buildings if building['building_id'] == id][0]
    room = input(f"For which room? Choose among these: {rooms}\n>>")
    possible_controls = ['heating', 'ventilation', 'lighting', 'people_level']
    control_type = input(f"What kind of control? Choose among these: {possible_controls}\n>>")

    found = False
    for control in controls:
        if control['building_id'] == id and control['room_id'] == room and control['control_type'] == control_type:
            found = True
            break
    if found:
        raise Exception("Control already present in our system")
    else:
        to_add = {
                    "control_id": str(int(controls[-1]['control_id']) + 1),
                    "building_id": id,
                    "room_id": room,
                    "control_type": control_type}
        with open("./actuators.json", "w") as file:
            controls.append(to_add)
            json.dump(controls, file, indent=4)
        print("Control added!")