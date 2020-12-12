from flask import Flask, make_response, request, jsonify, abort
from gevent.pywsgi import WSGIServer
from marshmallow import ValidationError

from app import app
from app import User, Event, Calendar
from schemas import UserToCreate, EventToCreate, user_schema, event_schema, events_schema, Group,  _id, userdata_schema, EventToUpdate, userdataa_schema
from app import db
from werkzeug.security import generate_password_hash
from flask_bcrypt import generate_password_hash

@app.route('/api/v1/hello-world-10')
def helloWord():
    return make_response("<H1>Hello Word 10</H1>", 200)


# ---------------EVENT----------------------
# http://127.0.0.1:5000/event

@app.errorhandler(404)
def http_404_handler(error):
    return jsonify(error=str(error)), 404


@app.errorhandler(400)
def http_400_handler(error):
    return jsonify(error=str(error)), 400


@app.errorhandler(405)
def http_405_handler(error):
    return jsonify(error=str(error)), 405


# good 400
@app.route("/event", methods=["POST"])
def add_event():
    if request.method == 'POST':

        event_data = request.args

        name = event_data.get('name')
        date = event_data.get('date')
        author = event_data.get('author')

        try:
            EventToCreate().load(event_data)
        except ValidationError:
            abort(400, description="Invalid Group")

        new_event = Event(name=name, date=date, author=author)

        db.session.add(new_event)
        db.session.commit()

        new_group = Calendar(user_id=author, event_id=new_event.id)

        db.session.add(new_group)
        db.session.commit()
        return jsonify(_id().dump(new_event))

    else:
        abort(405, description="Method Not Allowed")


# http://127.0.0.1:5000//event/findByDate/23.11.2022
@app.route("/event/findByDate/<string:date>", methods=["GET"])
def event_by_date(date):
    event = Event.query.filter_by(date=date).first()
    if event is None:
        abort(404, description="Event not found")

    all_events = Event.query.filter_by(date=date).all()

    result = events_schema.dump(all_events)

    return events_schema.jsonify(result)


# good
@app.route("/event/<int:id>", methods=["GET"])
def event_by_id(id):
    event = Event.query.get(id)

    if event is None:
        abort(404, description="Event not found")

    return event_schema.jsonify(event)


# http://127.0.0.1:5000/event/7?name=Dse&date=21.12.2023
@app.route("/event/<id>", methods=["PUT"])
def update_event_with_form_data(id):
    event_data = request.args
    up_event = Event.query.get(id)
    if Event.query.filter_by(id=id).first() is None:
        abort(404, description="User not found")
    up_event.name = event_data.get('name')
    up_event.date = event_data.get('date')

    try:
        EventToUpdate().load(event_data)
    except ValidationError:
        abort(400, description="Invalid Group")
    db.session.commit()

    return event_schema.jsonify(up_event)


# good
@app.route("/event/<int:id>", methods=["DELETE"])
def delete_event(id):
    event = Event.query.get(id)
    if event is None:
        abort(404, description="Event not found")

    Calendar.query.filter_by(event_id=id).delete()

    db.session.delete(event)
    db.session.commit()

    return event_schema.jsonify(event)


@app.route("/event/group/<int:id>", methods=["GET"])
def list_users_of_event(id):
    event = Event.query.filter_by(id=id).first()
    if event is None:
        abort(404, description="Event not found")
    result = []
    event_groups = Calendar.query.filter_by(event_id=id).all()

    for o in event_groups:
        groups = User.query.filter_by(id=o.user_id).all()
        result.append(userdata_schema.dump(groups))

    return jsonify(result)


# ---------------USER----------------------

# http://127.0.0.1:5000/user
# good
@app.route("/user", methods=["POST"])
def create_user():
    user_data = request.args

    username = user_data.get('username')
    firstName = user_data.get('firstName')
    lastName = user_data.get('lastName')
    email = user_data.get('email')
    password = user_data.get('password')
    phone = user_data.get('phone')

    try:
        UserToCreate().load(user_data)
    except ValidationError:
        abort(400, description="Invalid Group")

    hash_password = generate_password_hash(password)
    new_user = User(username=username, firstName=firstName, lastName=lastName, email=email, password=hash_password,
                    phone=phone)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(_id().dump(new_user))


@app.route("/user/login", methods=["GET"])
def login():
    # 400 error
    pass


@app.route("/user/logout", methods=["GET"])
def logout():
    pass


# good
@app.route("/user/<id>", methods=["GET"])
def user_by_name(id):
    user = User.query.get(id)

    if user is None:
        abort(404, description="User not found")

    return userdataa_schema.jsonify(user)


# http://127.0.0.1:5000/user/6?username=rr&firstName=De&lastName=e&email=er@ema.com&password=1234354678&phone=1232413452
@app.route("/user/<user_id>", methods=["PUT"])
def update_user(user_id):
    user_data = request.args
    up_user = User.query.get(user_id)
    if User.query.filter_by(id=user_id).first() is None:
        abort(404, description="User not found")
    up_user.username = user_data.get('username')
    up_user.firstName = user_data.get('firstName')
    up_user.lastName = user_data.get('lastName')
    up_user.email = user_data.get('email')
    up_password = user_data.get('password')
    up_user.phone = user_data.get('phone')
    try:
        UserToCreate().load(user_data)
    except ValidationError:
        abort(400, description="Invalid Group")
    up_user.password = generate_password_hash(up_password)


    db.session.commit()
    return user_schema.jsonify(up_user)


# good
@app.route("/user/<int:id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.get(id)
    if user is None:
        abort(404, description="User not found")
    Calendar.query.filter_by(user_id=id).delete()
    Event.query.filter_by(author=id).delete()

    db.session.delete(user)
    db.session.commit()

    return user_schema.jsonify(user)


@app.route("/user/group/<int:id>", methods=["GET"])
def list_events_of_user(id):
    user = User.query.filter_by(id=id)
    if user is None:
        abort(404, description="User not found")
    result = []
    user_groups = Calendar.query.filter_by(user_id=id).all()
    for o in user_groups:
        groups = Event.query.filter_by(id=o.event_id).all()

        result.append(events_schema.dump(groups))
    return jsonify(result)


# ---------------Group----------------------


@app.route("/calendar/group", methods=["POST"])
def group_of_users():
    group_data = request.args

    user_id = group_data.get('user_id')
    event_id = group_data.get('event_id')
    try:
        Group().load(group_data)

    except ValidationError:
        abort(400, description="Invalid Group")
    new_group = Calendar(user_id=user_id, event_id=event_id)

    db.session.add(new_group)
    db.session.commit()

    return jsonify(Group().dump(new_group))


# good 400 404
@app.route("/calendar/group/<int:event_id>", methods=["DELETE"])
def delete_group(event_id):
    group = Calendar.query.get(event_id)
    if group is None:
        abort(404, description="Group not found")
    Calendar.query.filter_by(event_id=event_id).delete()
    db.session.commit()
    return 'Delete success'


print('http://127.0.0.1:5000/api/v1/hello-world-10')
server = WSGIServer(('127.0.0.1', 5000), app)
server.serve_forever()


