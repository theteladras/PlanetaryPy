#ABOUT

A small playground app, based on Flask. What this app has for a goal is to allow the user to get, update, delete data about ceratin planets they insert into the database, aswell as having a registration system, which is needed, since not authenticated users can not submit changes to the databse.

#Installation

1) Clone the project from the repo.
2) Install all the required deppendencies.
3) run the app

###Additional:

4) If you have not created the DB, you will need to run - python db_create - from the directory of the app, in order to initialize a databse (type of the db is SQLite)
5) To add some seed data to the databse - python db_seed - from the directory of the app
6) Drop the whole databse by running - python db_drop

#GOTHROUGH:
  1) install python
  2) on windows setup the env path for pip
  3) install virtualenv - pip install virtualenv
  3.5) virtualenv -p python
  4) setup a virtual env in project - python -m virtualenv env
  5) activate the virtualenv in project - . ./env/Scripts/activate or on windows env\Scripts\Activate
  6) instal flaks - pip install flask
  7) export environment variables - command line: export APP_SETTINGS=config.cfg
  8) generate requirements file - pip freeze > requirements.txt
  9) install all deppendencies - pip install -r requirements.txt
  10) run by simply calling - python app.py - from the terminal in the directory of the project