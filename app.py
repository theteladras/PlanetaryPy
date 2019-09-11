from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
from marshmallow import Schema, fields
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'planets.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# start our database
@app.cli.command('db_create')
def db_create():
    db.create_all()
    print("Database is live...")


# delete the whole database
@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print("Database dropped!")

# add some seed data / initalize data
@app.cli.command('db_seed')
def db_seed():
    planet1 = Planet(
        planet_name='Mercury',
        planet_type="Class D",
        home_star="Sol",
        mass=3.258e23,
        radius=3760,
        distance=67.24e6
    )

    planet2 = Planet(
        planet_name='Venus',
        planet_type="Class K",
        home_star="Sol",
        mass=4.867e24,
        radius=1516,
        distance=35.98e6
    )

    planet3 = Planet(
        planet_name='Earth',
        planet_type="Class M",
        home_star="Sol",
        mass=5.972e24,
        radius=3959,
        distance=92.96e6
    )

    db.session.add(planet1)
    db.session.add(planet2)
    db.session.add(planet3)

    test_user = User(
        first_name="William",
        last_name="Herschel",
        email="willi@test.com",
        password="pw"
    )

    db.session.add(test_user)
    db.session.commit()
    print("Database got the seed data...")


@app.route('/')
def hello_world():
    return 'Hello World'


@app.route('/data')
def simple():
    return jsonify(message="This is no data...")


@app.route('/not_found')
def not_found():
    return "", 404


@app.route('/params')
def params():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age < 18:
        return jsonify(message="Sorry " + name + ", you are not old enough."), 401
    else:
        return jsonify(message="Welcome " + name + ", you are old enough.")


@app.route('/params/<string:name>/<int:age>')
def target(name: str, age: int):
    if age < 18:
        return jsonify(message="Sorry " + name + ", you are not old enough."), 401
    else:
        return jsonify(message="Welcome " + name + ", you are old enough.")


@app.route('/planets', methods=['GET'])
def planets():
    planets_list = Planet.query.all()
    result = planets_schema.dump(planets_list)
    return {"planets": result}


print(">>>>>>>>>>>>>>>>>>>>>> ", db)

# databse models


class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


class Planet(db.Model):
    __tablename__ = "planets"
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Str()
    password = fields.Str()


class PlanetSchema(Schema):
    planet_id = fields.Int(dump_only=True)
    planet_name = fields.Str()
    planet_type = fields.Str()
    home_star = fields.Str()
    mass = fields.Float()
    radius = fields.Float()
    distance = fields.Float()


user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)

if __name__ == '__main__':
    app.run(debug=True)
