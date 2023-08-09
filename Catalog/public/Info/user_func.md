# User Catalog
In this page are reported the definition of a user and all functionalities related. A user can act ... 

---

### User architecture

Each of the devices has the following characteristics:

- user id
- password
- is Super User
- set of Buildings the user has access to
- name
- surname


### User functionalities

Functionalities to get information of a user are available.
- You can retrieve all users with the command:\
<span style="color:green"> *http://127.0.0.1:9096/users?id=all* </span>
- You can retrieve a single user by knowing its id with the command:\
<span style="color:green">*http://127.0.0.1:9096/device?id=USERID* </span>
- <span style="color:red">*TODO* </span> aggiungere altri comandi
- You can perform a POST/PUT to insert/modify a user at the url:\
<span style="color:green">*http://127.0.0.1:9096/user* </span>\
wih the following json format:

```javascript
{
  "user_id": "x1",
  "password": "xyz"
  "name": "Mario",
  "surname": "Rossi",
  "building_ids": [y1, y2, y3],
  "is_super": True,
  
}
```


- You can perform a DELETE to delete a user at the url:\
<span style="color:green">*http://127.0.0.1:9096/device?id=USERID* </span>

