from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from sqlalchemy import ForeignKey
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

# making the outline of the user table in the database that consists of id, username, and password columns
class User(db.Model, UserMixin):
  # this column is the row identifier
  # not setting the username as the primary key in case the user edits it, it's just not good practice
  id = db.Column(db.Integer, primary_key = True)
  # there must be something in the username column, hence not nullable, each person has a different username
  username = db.Column(db.String(30), nullable = False, unique = True)
  # same goes for the password
  password = db.Column(db.String(30), nullable = False)

# making the outline of the model table in the database
# *************************************FOR THE WRITEUP:********************************************* 
# I chose to make this a table rather than a separate database because of the clear dependency in the data,
# namely the problems being related to specific users. There is no need to have access to the problems without
# having access to the users themselves, so it can be in the same database. There is not that much data either so
# it makes sense to keep it in the same database.
class Problem(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  # adding a foreign key so I can connect the problems to specific users
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
  problem_title = db.Column(db.Text, nullable = False)
  problem_text = db.Column(db.Text, nullable = False)
  # store solutions as strings and parse them later based on problem type
  # *************************************FOR THE WRITEUP:********************************************* 
  # This makes more sense because it's easier to parse one solution later than to deal with multiple
  # problem types within a database. This would either require more fields within the table, a complicated
  # way to address the differences in parsing the solutions, or different tables for each problem type, all
  # of which seemed wasteful. This is why I decided to stick to having a string.
  problem_solution = db.Column(db.Text, nullable = False)
  # *************************************FOR THE WRITEUP:********************************************* 
  # These two categories seemed to be the most plausible to include within my app because the other ones
  # are happening at a more subconscious level.
  problem_define = db.Column(db.Text, nullable = False)
  problem_encode = db.Column(db.Text, nullable = False)
  # adding confidence and mastery fields for computing these aspects
  problem_confidence = db.Column(db.Text, default = 0)
  problem_mastery = db.Column(db.Text, default = 0.0)
  # explaining the relationship between the user and the problems - the users will have problems assigned
  # to them. Problems will hold a list of Problem objects associated with the user. Use lazy=True to not
  # query immediately but rather once the problems are needed.
  user = db.relationship('User', backref='problems', lazy=True)

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
    
# making the outline of the edit account form
class Editaccount_form(FlaskForm):
  # old username input to make the user easier to find
  old_username = StringField(validators = [InputRequired(), Length(min = 3, max = 25)], render_kw={"placeholder":"Old username"})
  # old password input for security
  old_password = PasswordField(validators = [InputRequired(), Length(4, 15)], render_kw={"placeholder":"Old password"})
  # user changes what they want to change
  new_username = StringField(render_kw={"placeholder":"New username (if applicable)"})
  new_password = PasswordField(render_kw={"placeholder":"New password (if applicable)"})
  submit = SubmitField("Change")

  # if there is a mismatch with the old credentials, don't allow changes
  def credential_mismatch(self, old_username, old_password):
    user = User.query.filter_by(username = old_username.data).first
    if user == None:
      raise ValidationError("Old credentials incorrect.")
    # check if the hashed password is the same as user input
    if bcrypt.check_password_hash(user.password, old_password.data) == False:
      raise ValidationError("Old credentials incorrect.")

# making the outline of the problem form
#class Problem_form(FlaskForm):

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
      # checking the hashed password against the password from the form
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

@app.route('/editaccount', methods = ['GET','POST'])
@login_required
def editaccount():
  form = Editaccount_form()

  if form.validate_on_submit():
      username = form.old_username.data
      password = hash_password = bcrypt.generate_password_hash(form.old_password.data)
      # if the password data is updated, change to this new password
      if form.new_password.data != None:
        # check size
        if(len(form.new_password.data)>=4 and len(form.new_password.data)<=15):
          hash_password = bcrypt.generate_password_hash(form.new_password.data)
      # similar if username changes
      if form.new_username.data != None:
        # check size
        if(len(form.new_username.data)>=3 and len(form.new_username.data)<=25):
          username = form.new_username.data
      # look up the user in the database
      user = User.query.filter_by(username = form.old_username.data).first()
      # if user is not none, update information
      if user != None:
        user.username = username
        user.password = hash_password
      # commit the changes
      db.session.commit()
      #redirect to the dashboard page
      return redirect(url_for('dashboard'))

  return render_template('editaccount.html', form = form)

if __name__ == "__main__":
  app.run(host = '0.0.0.0', debug = True)