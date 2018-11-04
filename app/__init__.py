from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_restful import Resource, Api, reqparse
from os import listdir
from os.path import isfile, join

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
admin = Admin(app)
api = Api(app)

from app import routes, models, errors
from app.models import *

class OrderModelView(ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.username == 'admin':
            return True

        return False

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('admin'))

def upload_list():
    return [file for file in listdir(app.config['UPLOAD_FOLDER']) if isfile(join(app.config['UPLOAD_FOLDER'], file))]

admin.add_view(OrderModelView(models.User, db.session))
admin.add_view(OrderModelView(models.Order, db.session))
admin.add_view(OrderModelView(models.Notification, db.session))

app.jinja_env.globals.update(upload_list=upload_list)

api.add_resource(LoginAPI, '/api/login')
api.add_resource(UserAPI, '/api/users/<int:user_id>')
api.add_resource(UsersAPI, '/api/users')
api.add_resource(OrderAPI, '/api/users/<int:user_id>/orders')
api.add_resource(NotificationsAPI, '/api/notifications')
