# Building Catalog
In this page are reported the definition of a Building and all functionalities related.

---

### Building architecture

Each of the buildings has the following characteristics:

- building id
- building type (short description)
- all rooms


### Building functionalities

Functionalities to get information of a building are available.
- You can retrieve all device with the command:\
<span style="color:green"> *http://127.0.0.1:9096/building?id=all* </span>
- You can retrieve a single sensor by knowing its id with the command:\
<span style="color:green">*http://127.0.0.1:9096/building?id=BUILDINGID* </span>
- <span style="color:red">*TODO* </span> aggiungere altri comandi
- You can perform a POST/PUT to insert/modify a building at the url:\
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

Note: a building can be inserted by authorized users only (Super Users).

- You can perform a DELETE to delete a building from a room of a building at the url:\
<span style="color:green">*http://127.0.0.1:9096/building?id=BUILDINGID* </span>

