from flask_bcrypt import generate_password_hash
from marshmallow import validate, Schema, fields

from flask_marshmallow import Marshmallow
from app import app

ma = Marshmallow(app)


class UserToCreate(ma.Schema):
    id = fields.Integer()
    username = fields.String(required=True)
    firstName = fields.String(required=True)
    lastName = fields.String(required=True)
    email = fields.String(required=True, validate=validate.Email())
    password = fields.String(required=True)
    phone = fields.String(required=True)


user_schema = UserToCreate()


class Userdata(ma.Schema):
    id = fields.Integer()
    username = fields.String(required=True)
    firstName = fields.String(required=True)
    lastName = fields.String(required=True)
    email = fields.String(required=True, validate=validate.Email())
    phone = fields.String(required=True, validate=validate.Length(10))


userdataa_schema = Userdata()
userdata_schema = Userdata(many=True)


class _id(ma.Schema):
    id = fields.Integer()


class EventToCreate(ma.Schema):
    id = fields.Integer()
    name = fields.String(required=True)
    date = fields.String(required=True, validate=validate.Regexp(r"^\d{2}.\d{2}.\d{4}$"), format='%d.%m.%Y')
    author = fields.Integer(required=True)


event_schema = EventToCreate()
events_schema = EventToCreate(many=True)


class EventToUpdate(ma.Schema):
    name = fields.String(required=True)
    date = fields.String(required=True, validate=validate.Regexp(r"^\d{2}.\d{2}.\d{4}$"), format='%d.%m.%Y')


class Group(ma.Schema):
    user_id = fields.Integer()
    event_id = fields.Integer()


