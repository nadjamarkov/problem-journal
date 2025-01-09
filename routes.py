from app import bcrypt
from flask import flash, render_template, redirect, url_for, jsonify, request
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db
from forms import Login_form, Signup_form, Editaccount_form, Record_form
from models import User, Problem, Folder
from wtforms import ValidationError
from parsers import shunting_yard, evaluate_rpn, match
from datetime import datetime, timezone

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
      print("VALID!!!")
      print(form.errors)
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
  # put all the folder choices into the form
  form.old_folder.choices = Record_form.populate_folders(current_user.id)

  if form.validate_on_submit():
    # variable for saving the folder id in case of a new folder
    folder_id = None
    # check if the user added a new folder
    if form.new_folder.data:
      new_folder = Folder(name=form.new_folder.data, user_id=current_user.id, folder_type=form.problem_type.data)
      db.session.add(new_folder)
      db.session.commit()
      folder_id = new_folder.id
    # otherwise the user wants to use one of the old folders
    else:
      folder_id = form.old_folder.data

    # add the problem to the database
    new_problem = Problem(problem_title = form.problem_title.data, problem_text = form.problem_text.data, problem_type = form.problem_type.data, problem_define = form.problem_define.data, problem_encode = form.problem_encode.data, problem_solution = form.problem_solution.data, user_id = current_user.id, folder_id = folder_id, last_practiced = datetime.now(timezone.utc), last_updated = datetime.now(timezone.utc))

    db.session.add(new_problem)
    db.session.commit()

    # update the mastery of the folder the new problem is in
    folder = Folder.query.filter_by(id=folder_id).first()
    folder.folder_mastery += new_problem.problem_mastery

    return redirect(url_for('dashboard'))
  
  return render_template('record.html', form = form)

  
@app.route('/retrieve', methods = ['GET','POST'])
@login_required
def retrieve():
  # find which problem type the user clicked on
  selected_type = request.args.get('type', None)

  # if a type is selected, filter folders by folder_type
  if selected_type:
      folders = Folder.query.filter_by(folder_type=selected_type).all()
  # otherwise show all folders
  else:
      folders = Folder.query.all()

  return render_template('retrieve.html', folders=folders)

# implement spaced repetition for retrieving problems
@app.route('/api/start_review', methods=['POST'])
@login_required
def start_review():
  data = request.get_json()
  problem_id = data.get('problem_id')
  problem = Problem.query.get(problem_id)

  if problem:
    current_time = datetime.now(timezone.utc)
    # make sure the times are timezone aware
    if problem.last_practiced.tzinfo is None:
      problem.last_practiced = problem.last_practiced.replace(tzinfo=timezone.utc)
    if problem.last_updated.tzinfo is None:
      problem.last_updated = problem.last_updated.replace(tzinfo=timezone.utc)
    # calculate the time difference since the last update
    time_diff = (current_time - problem.last_updated ).days

    problem_data = {
      'id': problem.id, 'title': problem.problem_title, 'text': problem.problem_text, 'solution': problem.problem_solution, 'define':problem.problem_define, 'encode':problem.problem_encode, 'mastery':problem.problem_mastery, 'type':problem.problem_type, 'time_since_practiced':time_diff
    }

    return jsonify(problem_data)
 
  else:
    return jsonify({'error': 'Folder not found'}), 404
  
# decrease problem mastery if it was last accessed a long time ago before showing them to the user
@app.route('/api/start_practice', methods=['POST'])
@login_required
def start_practice():
    data = request.get_json()
    folder_id = data.get('folder_id')
    folder = Folder.query.get(folder_id)
    
    if folder:
        current_time = datetime.now(timezone.utc)

        # loop through all problems in the folder
        for problem in folder.problems:
            # make sure the times are timezone aware
            if problem.last_practiced.tzinfo is None:
               problem.last_practiced = problem.last_practiced.replace(tzinfo=timezone.utc)
            if problem.last_updated.tzinfo is None:
               problem.last_updated = problem.last_updated.replace(tzinfo=timezone.utc)

            # calculate the time difference since the last update
            time_diff = (current_time - problem.last_updated ).days

            # if the problem hasn't been practiced since the last update, decrease mastery
            if ((current_time - problem.last_practiced).days>0):
              # decrease mastery by 0.05 for every day it hasn't been practiced since the last update
              problem.problem_mastery -= time_diff * 0.05

              if problem.problem_mastery < 0:
                problem.problem_mastery = 0

            problem.last_updated = current_time
        
        # recalculate folder mastery
        folder.folder_mastery = sum([problem.problem_mastery for problem in folder.problems]) / len(folder.problems)

        if folder.folder_mastery < 0:
            folder.folder_mastery = 0

        # commit changes
        db.session.commit()

        folder_data = {
          'id': folder.id,
          'mastery': folder.folder_mastery,
          'problems': [{'id': problem.id, 'title': problem.problem_title, 'text': problem.problem_text, 'solution': problem.problem_solution, 'define':problem.problem_define, 'encode':problem.problem_encode, 'mastery':problem.problem_mastery, 'type':problem.problem_type, 'time_since_practiced':time_diff} for problem in folder.problems]
        }

        return jsonify(folder_data)
    
    else:
      return jsonify({'error': 'Folder not found'}), 404
    
# checking the answer for algebraic questons
@app.route('/check_answer', methods=['POST'])
def check_answer():
  user_input = request.json['user_input']
  correct_solution = request.json['correct_solution']
  problem_type = request.json['problem_type']
  problem_define = request.json['problem_define']
  problem_encode = request.json['problem_encode']

  # check if the problem is algebra
  if problem_type == "Algebra":
    # if the solution is supposed to just be a number, check the solutions as strings
    if problem_define == "Number":
      if user_input == correct_solution:
        return jsonify({'result': 'correct'})
      else:
        return jsonify({'result': 'incorrect'})
    # otherwise run shunting yard
    else:
      user_rpn = shunting_yard(user_input)
      correct_rpn = shunting_yard(correct_solution)

      user_result = evaluate_rpn(user_rpn)
      correct_result = evaluate_rpn(correct_rpn)
    
      # compare the results
      if round(user_result, 2) == round(correct_result, 2):
        return jsonify({'result': 'correct'})
      else:
        return jsonify({'result': 'incorrect'})
  
  # otherwise the problem is a regular expressions one
  else:
    # check if we're looking for a regular expression or writing down text and run the matching algorithm
    if problem_define == "Expression":
      print("I AM IN REGEX EXPRESSIONS")
      print(user_input)
      print(problem_encode)
      if match(user_input, problem_encode) == 1:
        return jsonify({'result': 'correct'})
      else:
        return jsonify({'result': 'incorrect'})
    else:
      if match(problem_encode, user_input) == 1:
        return jsonify({'result': 'correct'})
      else:
        return jsonify({'result': 'incorrect'})


# updating the mastery of the problem (and the folder) based on the answer
@app.route('/api/update_problem_mastery', methods=['POST'])
@login_required
def update_problem_mastery():
  data = request.get_json()
  problem_id = data.get('problem_id')
  help = data.get('help')
  folder_id = data.get('folder_id')

  # get the folder and the problem and update the mastery
  folder = Folder.query.get(folder_id)
  problem = Problem.query.get(problem_id)
  if problem:
      folder.folder_mastery -= (problem.problem_mastery/len(folder.problems))
      if folder.folder_mastery < 0:
         folder.folder_mastery = 0

      if help == 0:
        problem.problem_mastery += 0.3
      elif help == 1:
        problem.problem_mastery += 0.2
      elif help == 2:
        problem.problem_mastery += 0.1
      else:
        problem.problem_mastery -= 0.3

      # make sure that mastery doesn't go above one or below zero
      if problem.problem_mastery < 0:
        problem.problem_mastery = 0
      if problem.problem_mastery > 1:
        problem.problem_mastery = 1
      
      folder.folder_mastery += (problem.problem_mastery/len(folder.problems))
      if folder.folder_mastery > 1:
         folder.folder_mastery = 1
      
      # update the time that the problem was practiced
      problem.last_practiced = datetime.now(timezone.utc)

      # commit changes to the database
      db.session.commit()

      return jsonify({"status": "success", "mastery": problem.problem_mastery}), 200
  else:
      return jsonify({"error": "Problem not found"}), 404