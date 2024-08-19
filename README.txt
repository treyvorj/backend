Trace

Trace is a very simple tcp traceroute api built using fastapi, sqlalchemy, and postgresql

It allows you to create "site" objects comprising of a (unique) url and a name.
Once a site is created, a tcptraceroute test can be ran against it.

* Setup
1. clone the repo to a local directory
2. install postgresql and start the psql server
3. you can use app/standup_db.sql to initally create the db
4. create a python virtual environment
5. active your venv
6. run `pip install -r requirements.txt`
7. run `alembic upgrade head`
8. run `fastapi dev app/main.py`

visit http://127.0.0.1:8000/docs to test out the api
