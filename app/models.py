from flask import url_for, request
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource

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

    def get(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'filename': self.filename,
            'status': self.status
        }
        return data

    def put(self, data):
        for field in ['user_id', 'name', 'filename', 'status']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return '<order {}>'.format(self.id)

class UserGet(Resource):
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        data = {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'tutor_group': user.tutor_group
        }
        return data

class UserPut(Resource):
    def put(self, username, password, full_name, tutor_group):
        user = User(username=username, full_name=full_name, tutor_group=tutor_group)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        get_order = OrderGet()
        return get_order.get(user.id)

class OrderGet(Resource):
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

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
