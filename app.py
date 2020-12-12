from flask import Flask, make_response
from gevent.pywsgi import WSGIServer
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from sqlalchemy.orm import backref
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


class Calendar(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))

    event = db.relationship("Event", back_populates="users")
    user = db.relationship("User", back_populates="events")


# u = User(username='lu', firstName='Mary', lastName='N', email='mary@example.com', password='1111', phone='0971112233')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    firstName = db.Column(db.String, unique=False, nullable=False)
    lastName = db.Column(db.String, unique=False, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=False, nullable=False)
    phone = db.Column(db.String, unique=True, nullable=False)
    events = db.relationship("Calendar", back_populates="user")

    def __init__(self, username=None, firstName=None, lastName=None, email=None, password=None, phone=None):
        self.username = username
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.password = password
        self.phone = phone


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=False)
    date = db.Column(db.String, unique=False, nullable=True)
    author = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    users = db.relationship("Calendar", back_populates="event")

    def __init__(self, name=None, date=None, author=None):
        self.name = name
        self.date = date
        self.author = author




if __name__ == '__main__':
    manager.run()
