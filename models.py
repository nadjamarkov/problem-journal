from app import db
from flask_login import UserMixin
from sqlalchemy import ForeignKey

# making the outline of the user table in the database that consists of id, username, and password columns
class User(db.Model, UserMixin):
  # this column is the row identifier
  # not setting the username as the primary key in case the user edits it, it's just not good practice
  id = db.Column(db.Integer, primary_key = True)
  # there must be something in the username column, hence not nullable, each person has a different username
  username = db.Column(db.String(30), nullable = False, unique = True)
  # same goes for the password
  password = db.Column(db.String(30), nullable = False)
  # creating a relationship between the user and the folders
  #folders = db.relationship('Folder', backref='user', lazy=True)
  # creating a relationship between the user and the problems
  problems = db.relationship('Problem', backref='user', lazy = True)

# making the outline of the Folder table in the database
# *************************************FOR THE WRITEUP:********************************************* 
# I wanted to be able to save problems to specific folders for easier user access. This was done in 
# part to get me more comfortable with using databases, as I haven't built any database models before.
# On the other hand, it's also useful within the app as it gives me more functionality within it.
# Folders are connected to specific users and hold specific problems within them.
#class Folder(db.Model):
  #id = db.Column(db.Integer, primary_key = True)
  # adding a foreign key to connect the folders to specific users
  #user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable = False)
  # adding the name of the folder as a parameter
  #name = db.Column(db.Text, nullable = False)
  # folder mastery parameter, initially zero
  #folder_mastery = db.Column(db.Float, default = 0.0)
  # the folders will have problems assigned to them. Folders will hold a list of Problem objects associated with the user. 
  # Use lazy=True to not query immediately but rather once the problems are needed. Backref creates a reverse relationship,
  # so both folder.problems and problem.folder are available
  #problems = db.relationship('Problem', backref='folder', lazy=True) 

# making the outline of the Problem table in the database
# *************************************FOR THE WRITEUP:********************************************* 
# I chose to make this a table rather than a separate database because of the clear dependency in the data,
# namely the problems being related to specific users. There is no need to have access to the problems without
# having access to the users themselves, so it can be in the same database. There is not that much data either so
# it makes sense to keep it in the same database.
class Problem(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  # adding a foreign key so I can connect the problems to specific users
  user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable = False)
  # adding another foreign key so I can connect the problems to specific folders
  #folder_id = db.Column(db.Integer, ForeignKey('folder.id'), nullable = False)
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
  problem_confidence = db.Column(db.Float, default = 0)
  problem_mastery = db.Column(db.Float, default = 0.0)
  # save the specific problem type the user is inputing (algebra, graph, etc.)
  problem_type = db.Column(db.Text, nullable = False)
