# Device Catalog
In this page are reported the definition of a device and all functionalities related. A device works as an actuator and is installed within a room
of a building.

---

### Device architecture

Each of the devices has the following characteristics:

- device id
- control type
- topic
- building id
- room id


### Device functionalities

Functionalities to get information of a device are available.
- You can retrieve all device with the command:\
<span style="color:green"> *http://127.0.0.1:9096/device?id=all* </span>
- You can retrieve a single sensor by knowing its id with the command:\
<span style="color:green">*http://127.0.0.1:9096/device?id=DEVICEID* </span>
- <span style="color:red">*TODO* </span> aggiungere altri comandi
- You can perform a POST/PUT to insert/modify a device at the url:\
<span style="color:green">*http://127.0.0.1:9096/building* </span>\
wih the following json format:

```javascript
{
  "sensor_id": "x1",
  "building_id": "y1",
  "room_id": "z1",
  "control_type": "mechanical",
  "topic": "/your/topic"
}
```

Note: a device can be inserted by authorized users only (Super Users).

- You can perform a DELETE to delete a device from a room of a building at the url:\
<span style="color:green">*http://127.0.0.1:9096/device?id=DEVICEID* </span>

