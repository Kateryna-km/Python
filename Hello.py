from flask import Flask, make_response, request, jsonify, abort
from gevent.pywsgi import WSGIServer
from marshmallow import ValidationError

from app import app
from app import User, Event, Calendar
from schemas import UserToCreate, EventToCreate, user_schema, event_schema, events_schema, Group,  _id, userdata_schema, EventToUpdate, userdataa_schema
from app import db
from werkzeug.security import generate_password_hash
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, \
    jwt_refresh_token_required, get_jwt_identity, get_raw_jwt


app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
jwt = JWTManager(app)

blacklist = set()


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


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
@jwt_refresh_token_required
def add_event():
    if request.method == 'POST':
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()

        event_data = request.args

        name = event_data.get('name')
        date = event_data.get('date')
        author = user.id
        #author = event_data.get('author')

        #try:
        #    EventToCreate().load(event_data)
        #except ValidationError:
        #    abort(400, description="Invalid Group")

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
@jwt_required
def event_by_date(date):
    event = Event.query.filter_by(date=date).first()
    if event is None:
        abort(404, description="Event not found")

    all_events = Event.query.filter_by(date=date).all()

    result = events_schema.dump(all_events)

    return events_schema.jsonify(result)


# good
@app.route("/event/<int:id>", methods=["GET"])
@jwt_required
def event_by_id(id):
    event = Event.query.get(id)

    if event is None:
        abort(404, description="Event not found")

    return event_schema.jsonify(event)


# http://127.0.0.1:5000/event/7?name=Dse&date=21.12.2023
@app.route("/event/<int:id>", methods=["PUT"])
@jwt_refresh_token_required
def update_event_with_form_data(id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    event_data = request.args
    if Event.query.filter_by(id=id, author=user.id).first() is None:
        abort(404, description="Event not found")
    up_event = Event.query.get(id)
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
@jwt_refresh_token_required
def delete_event(id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if Event.query.filter_by(id=id, author=user.id).first() is None:
        abort(404, description="Event not found")
    event = Event.query.get(id)
    if event is None:
        abort(404, description="Event not found")

    Calendar.query.filter_by(event_id=id).delete()

    db.session.delete(event)
    db.session.commit()

    return event_schema.jsonify(event)


@app.route("/event/group/<int:id>", methods=["GET"])
@jwt_required
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

    if User.query.filter_by(username=username).first() is not None:
        return {'message': 'User {} already exists'.format(user_data['username'])}

    if User.query.filter_by(phone=phone).first() is not None:
        return {'message': 'Phone {} already exists'.format(user_data['phone'])}

    if User.query.filter_by(email=email).first() is not None:
        return {'message': 'Email {} already exists'.format(user_data['email'])}

    try:
        UserToCreate().load(user_data)
    except ValidationError:
        abort(400, description="Invalid Group")

    hash_password = generate_password_hash(password)
    new_user = User(username=username, firstName=firstName, lastName=lastName, email=email, password=hash_password,
                    phone=phone)
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)

    db.session.add(new_user)
    db.session.commit()

    return {'id': new_user.id, 'access token': access_token, 'refresh token': refresh_token}
#jsonify(_id().dump(new_user)),


@app.route("/user/login", methods=["POST"])
def login():
    data = request.args
    username = data.get('username')
    password = data.get('password')
    current_user = User.query.filter_by(username=username).first()
    if current_user is None:
        return {'message': 'User {} doesn\'t exist'.format(data['username'])}
    if check_password_hash(current_user.password, password):
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        return {'message': 'Logged in as {}'.format(current_user.username),
                'access token': access_token,
                'refresh_token': refresh_token}
    else:
        return {'message': 'Wrong password'}


@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    return {'access_token': create_access_token(identity=current_user)}


@app.route("/user/logout", methods=['DELETE'])
@jwt_refresh_token_required
#@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return {'message': 'Successfully logged out'}


# good
@app.route("/user/<id>", methods=["GET"])
@jwt_required
def user_by_name(id):
    user = User.query.get(id)

    if user is None:
        abort(404, description="User not found")

    return userdataa_schema.jsonify(user)


# http://127.0.0.1:5000/user/6?username=rr&firstName=De&lastName=e&email=er@ema.com&password=1234354678&phone=1232413452
#@app.route("/user/<user_id>", methods=["PUT"])
@app.route("/user/update", methods=["PUT"])
@jwt_refresh_token_required
def update_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    user_data = request.args
    up_user = User.query.get(user.id)
    if User.query.filter_by(id=user.id).first() is None:
        abort(404, description="User not found")
    try:
        UserToCreate().load(user_data)
    except ValidationError:
        abort(400, description="Invalid Group")
    up_user.username = user_data.get('username')
    up_user.firstName = user_data.get('firstName')
    up_user.lastName = user_data.get('lastName')
    up_user.email = user_data.get('email')
    up_password = user_data.get('password')
    up_user.phone = user_data.get('phone')
    up_user.password = generate_password_hash(up_password)

    db.session.commit()
    return user_schema.jsonify(up_user)


# good
#@app.route("/user/<int:id>", methods=["DELETE"])
@app.route("/user/delete", methods=["DELETE"])
@jwt_refresh_token_required
def delete_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if user is None:
        abort(404, description="User not found")
    if Calendar.query.filter_by(user_id=user.id).first() is not None:
        Calendar.query.filter_by(user_id=user.id).delete()
    Event.query.filter_by(author=user.id).delete()

    db.session.delete(user)
    db.session.commit()

    return user_schema.jsonify(user)


@app.route("/user/group/<int:id>", methods=["GET"])
@jwt_required
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
@jwt_refresh_token_required
def group_of_users():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    group_data = request.args

    user_id = int(group_data.get('user_id'))
    event_id = int(group_data.get('event_id'))
    event = Event.query.filter_by(author=user.id).first()
    if event is None or event_id != event.id:
        return {'message': 'Error access to event'}, 405

    try:
        Group().load(group_data)

    except ValidationError:
        abort(400, description="Invalid Group")

    if Calendar.query.filter_by(user_id=user_id, event_id=event_id).first() is not None:
        return {'message': 'Group with id user {} and id event {} already exists'.format(user_id, event_id)}
    new_group = Calendar(user_id=user_id, event_id=event_id)

    db.session.add(new_group)
    db.session.commit()

    return jsonify(Group().dump(new_group))


# good 400 404
@app.route("/calendar/group/<int:event_id>", methods=["DELETE"])
@jwt_refresh_token_required
def delete_group(event_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    group = Calendar.query.get(event_id)
    if group is None:
        abort(404, description="Group not found")

    if Event.query.filter_by(author=user.id, id=event_id) is None and group.user_id != user.id:
        return {'message': 'Error access to event'}, 405

    Calendar.query.filter_by(event_id=event_id).delete()
    db.session.commit()
    return 'Delete success'


print('http://127.0.0.1:5000/api/v1/hello-world-10')
server = WSGIServer(('127.0.0.1', 5000), app)
server.serve_forever()


