# Sensor Catalog
In this page are reported the definition of sensor and all functionalities related. A sensor is installed within a room
of a building.

---

### Sensor architecture

Each of the sensors has the following characteristics:

- sensor id
- measurement type
- topic
- building id
- room id


### Sensor functionalities

Functionalities to get information of a sensor are available.
- You can retrieve all sensors with the command:\
<span style="color:green"> *http://127.0.0.1:9096/sensor?id=all* </span>
- You can retrieve a single sensor by knowing its id with the command:\
<span style="color:green">*http://127.0.0.1:9096/sensor?id=SENSORID* </span>
- <span style="color:red">*TODO* </span> aggiungere altri comandi
- You can perform a POST/PUT to insert/modify a sensor at the url:\
<span style="color:green">*http://127.0.0.1:9096/sensor* </span>\
wih the following json format:

```javascript
{
  "sensor_id": "x1",
  "building_id": "y1",
  "room_id": "z1",
  "meas_type": "temperature",
  "topic": "/your/topic"
}
```

Note: a sensor can be inserted by authorized users only (Super Users).

- You can perform a DELETE to delete a sensor from a room of a building at the url:\
<span style="color:green">*http://127.0.0.1:9096/sensor?id=SENSORID* </span>

