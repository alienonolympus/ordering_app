from flask import url_for, request
from app import db, login, app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource, reqparse
import arrow, os, werkzeug

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    full_name = db.Column(db.String(64))
    tutor_group = db.Column(db.String(8))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def orders(self):
        return Order.query.filter_by(user_id=self.id)

    def __repr__(self):
            return '<user {}>'.format(self.username)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(128))
    filename = db.Column(db.String(128))
    status = db.Column(db.Integer)

    def __repr__(self):
        return '<order {}>'.format(self.id)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    content = db.Column(db.String(128))
    date = db.Column(db.String(128), default=arrow.utcnow().replace(hours=8).format())

    def __repr__(self):
        return '<notification {}>'.format(self.id)

class UserAPI(Resource):
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        data = {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'tutor_group': user.tutor_group
        }
        return data

class UsersAPI(Resource):
    def get(self):
        users = User.query.all()
        data = {}
        for user in users:
            data[str(user.id)] = {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'tutor_group': user.tutor_group
            }
        return data

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username')
        parser.add_argument('full_name')
        parser.add_argument('tutor_group')
        parser.add_argument('password')
        args = parser.parse_args()
        username, full_name, tutor_group, password = args['username'], args['full_name'], args['tutor_group'], args['password']
        user = User(username=username, full_name=full_name, tutor_group=tutor_group)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        args['id'] = user.id
        del args['password']
        args['password_hash'] = user.password_hash
        return args

class OrderAPI(Resource):
    def get(self, user_id):
        orders = Order.query.filter_by(user_id=user_id)
        data = {}
        for order in orders:
            data[order.id] = {}
            data[order.id]['user_id'] = user_id
            data[order.id]['name'] = order.name
            data[order.id]['filename'] = order.filename
            data[order.id]['status'] = order.status
        return data

    def post(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        args = parser.parse_args()
        print(args)
        order = Order(user_id=user_id, name=args['name'], status=0)
        db.session.add(order)
        db.session.flush()
        uploaded_file = request.files['file']
        filename = str(order.id) + '_' + uploaded_file.filename
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        order.filename = filename
        db.session.commit()
        args['id'] = order.id
        args['user_id'] = order.user_id
        args['filename'] = order.filename
        args['status'] = order.status
        return args

class NotificationsAPI(Resource):
    def get(self):
        notifications = Notification.query.all()
        data = {}
        for notification in notifications:
            data[str(notification.id)] = {
                'id': notification.id,
                'title': notification.title,
                'content': notification.content,
                'date': notification.date
            }
        return data

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
