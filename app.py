from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
from marshmallow import Schema, fields
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] = 'this-is-a-secret'
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config.from_envvar('APP_SETTINGS')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False


db = SQLAlchemy(app)
jwt = JWTManager(app)
mail = Mail(app)

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


@app.route('/register', methods=['POST'])
def register():
    req_data = request.get_json()
    email = req_data['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message="E-mail already in use.")
    else:
        first_name = req_data['first_name']
        last_name = req_data['last_name']
        password = req_data['password']
        user = User(first_name=first_name, last_name=last_name,
                    email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="Successfully registered.")


@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']
    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login success!", token=access_token)
    return jsonify(message="Login failed."), 401


@app.route('/reset_password/<string:email>', methods=['GET'])
def reset_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message("Password is: " + user.password,
                      sender="admin@planetary.com", recipients=[email])
        mail.send(msg)
        return jsonify(message="Password sent to: " + email)
    return jsonify(message="This E-mail is not registered."), 401


@app.route('/planet_details/<int:planet_id>', methods=['GET'])
def planet_details(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(result)
    return jsonify(message="The planet with the provided ID does not exist."), 404


@app.route('/add_planet', methods=['POST'])
def add_planet():
    planet_name = request.json['planet_name']
    test = Planet.query.filter_by(planet_name=planet_name).first()
    if test:
        return jsonify("There is already a planet registered bythat name"), 409
    planet_type = request.json['planet_type']
    home_star = request.json['home_start']
    mass = float(request.json['mass'])
    radius = float(request.json['radius'])
    distance = float(request.json['distance'])

    new_planet = Planet(
        planet_name=planet_name,
        planet_type=planet_type,
        home_star=home_star,
        mass=mass,
        radius=radius,
        distance=distance
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(Message="Planet added!"), 201


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
