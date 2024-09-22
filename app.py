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

# to create these changes type into the python console
# from app import db, app
# app.app_context().push()
# db.create_all()
# exit()
# to check if it worked type in
# sqlite3 db.sqlite
# .tables
# .exit

# making the outline of the database (a model) that consists of id, username, and password columns
class User(db.Model, UserMixin):
  # this column is the row identifier
  # not setting the username as the primary key in case the user edits it, it's just not good practice
  id = db.Column(db.Integer, primary_key = True)
  # there must be something in the username column, hence not nullable, each person has a different username
  username = db.Column(db.String(30), nullable = False, unique = True)
  # same goes for the password
  password = db.Column(db.String(30), nullable = False)

# making the outline of the log in form
class Login_form(FlaskForm):
  # the validators are used to make sure we get the values we want, in the format we want
  # render_kw sets the default parameters for the field
  username = StringField(validators = [InputRequired(), Length(min = 3, max = 25)], render_kw={"placeholder":"Username"})
  password = PasswordField(validators = [InputRequired(), Length(4, 15)], render_kw={"placeholder":"Password"})
  submit = SubmitField("Log In")

# making the outline of the sign up form
class Signup_form(FlaskForm):
  username = StringField(validators = [InputRequired(), Length(min = 3, max = 25)], render_kw={"placeholder":"Username"})
  password = PasswordField(validators = [InputRequired(), Length(4, 15)], render_kw={"placeholder":"Password"})
  submit = SubmitField("Sign Up")

  def unique_username(self, username):
    # .query is querying the User model, and then it applies a filter that finds if any username field (username) is equal to the
    # data from the WTF form (username.data) and retrieving the first instance of this or None if nothing matches
    unique = User.query.filter_by(username = username.data).first()
    if unique != None:
      raise ValidationError("That username has already been taken.")

# defining which pages to return when
@app.route('/')

def home():
  return render_template('home.html')

@app.route('/demo')
def demo():
  return render_template('demo.html')

# the GET method is the default method that is used. In this case, it is used to fill out the forms. The POST method sends data to the server.
@app.route('/login', methods=['GET','POST'])
def login():
  # passing in the forms
  form = Login_form()
  # adding the form to the html template
  return render_template('login.html', form = form)

@app.route('/signup', methods=['GET','POST'])
def signup():
    form = Signup_form()

    if form.validate_on_submit():
      # hashing to make the sign up process secure
      hash_password = bcrypt.generate_password_hash(form.password.data)
      new_user = User(username = form.username.data, password = hash_password)
      # add new user to the database
      db.session.add(new_user)
      # commit the changes
      db.session.commit()
      #redirect to the login page
      return redirect(url_for('login'))

    return render_template('signup.html', form = form)

if __name__ == "__main__":
  app.run(host = '0.0.0.0', debug = True)