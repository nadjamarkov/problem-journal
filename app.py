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

# the login manager holds settings needed for logging in
login_manager = LoginManager()
# configure it to the application object
login_manager.init_app(app)

# takes a user_id and returns a User object that's being used in this section
# user_id gets passed as a string, so we need to convert it to an integer because that's how primary keys
# are stored in this database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
  # validate_on_submit lets us check if the user clicked the submit button as well as if eve
  if form.validate_on_submit():
    # check if the user is in the database
    user = User.query.filter_by(username = form.username.data).first()
    # if user is not None
    if user != None:
      # checking the hashed thing against the password from the form
      if bcrypt.check_password_hash(user.password, form.password.data):
        # log the user in
        login_user(user)
        #redirect to the dashboard page
        return redirect(url_for('dashboard'))
  
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

@app.route('/dashboard', methods=['GET','POST'])
# We can only access this once the user is logged in
@login_required
def dashboard():
  return render_template('dashboard.html')

@app.route('/logout', methods = ['GET', 'POST'])
# we have to be logged in in order to log out
@login_required
def logout():
  # no need to pass the actual user into logout_user
  logout_user()
  # go back to the login page
  return redirect(url_for('login'))

if __name__ == "__main__":
  app.run(host = '0.0.0.0', debug = True)