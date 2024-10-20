from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import os

#test

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

# the login manager holds settings needed for logging in
login_manager = LoginManager()
# configure it to the application object
login_manager.init_app(app)

# import the database models
from models import User

# takes a user_id and returns a User object that's being used in this section
# user_id gets passed as a string, so we need to convert it to an integer because that's how primary keys
# are stored in this database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# import the routes
from routes import *

if __name__ == "__main__":
  app.run(host = '0.0.0.0', debug = True)