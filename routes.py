from app import bcrypt
from flask import flash, render_template, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db
from forms import Login_form, Signup_form, Editaccount_form, Record_form
from models import User, Problem

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

@app.route('/record', methods = ['GET', 'POST'])
@login_required
def record():
  # access the record form
  form = Record_form()

  # iterate through all of the folders that already exist and present them as options
  #folder_choices = []
  #for folder in current_user.folders:
    #folder_choices.append((folder.id, folder.name))
  #form.old_folder.choices = folder_choices

  if form.validate_on_submit():
    # check if the user added a new folder
    #if form.new_folder.data:
      #new_folder = Folder(name = form.new_folder.data, user_id = current_user.id)
      #db.session.add(new_folder)
      # use flush to add this immediately and not wait to close file
      #db.session.flush()
      # set the new problem
      #new_problem = Problem(problem_title = form.problem_title.data, problem_text = form.problem_text.data, problem_type = form.problem_type.data, problem_define = form.problem_define.data, problem_encode = form.problem_encode.data, problem_solution = form.problem_solution.data, folder_id = new_folder.id, user_id = current_user.id)
      # add the new problem to the database
      #db.session.add(new_problem)
    # otherwise add to the folder that the user wanted to add it to
    #else:
    new_problem = Problem(problem_title = form.problem_title.data, problem_text = form.problem_text.data, problem_type = form.problem_type.data, problem_define = form.problem_define.data, problem_encode = form.problem_encode.data, problem_solution = form.problem_solution.data, user_id = current_user.id)
    db.session.add(new_problem)
    
    db.session.commit()
    return redirect(url_for('dashboard'))

  return render_template('record.html', form = form)
