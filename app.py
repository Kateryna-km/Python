from flask import Flask, make_response
from gevent.pywsgi import WSGIServer
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#app.config.from_pyfile('config.cfg')

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


Calendar = db.Table('events',
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
                    )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    firstName = db.Column(db.String, unique=False, nullable=False)
    lastName = db.Column(db.String, unique=False, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=False, nullable=False)
    phone = db.Column(db.String, unique=True, nullable=False)
    Calendar = db.relationship('Event', secondary=Calendar, lazy='subquery',
                               backref=db.backref('users', lazy=True))


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=False)
    date = db.Column(db.String, unique=False, nullable=False)
    event_date_in_calendar = db.Column(db.String, unique=False, nullable=False)
    autor = db.Column(db.Integer, unique=True, nullable=False)


#@app.route('/api/v1/hello-world-10')
#def hello_word():
#    return 'Hello World 5'


if __name__ == '__main__':
    manager.run()
#print('http://127.0.0.1:5000/api/v1/hello-world-10')
#server = WSGIServer(('127.0.0.1', 5000), app)
#server.serve_forever()