from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError
from models import User, Problem, Folder
from app import bcrypt

# making the outline of the log in form
class Login_form(FlaskForm):
  # the validators are used to make sure we get the values we want, in the format we want
  # render_kw sets the default parameters for the field
  username = StringField(validators = [InputRequired(), Length(min = 3, max = 25)], render_kw={"placeholder":"Username"})
  password = PasswordField(validators = [InputRequired(), Length(4, 15)], render_kw={"placeholder":"Password"})
  submit = SubmitField("Log In")

# making the outline of the sign up form
class Signup_form(FlaskForm):
  # making sure the username is unique
  def unique_username(self, username):
    # .query is querying the User model, and then it applies a filter that finds if any username field (username) is equal to the
    # data from the WTF form (username.data) and retrieving the first instance of this or None if nothing matches
    unique = User.query.filter_by(username = username.data).first()
    if unique != None:
      print("Username already taken.")
      raise ValidationError("That username has already been taken.")
    print("Username is unique.")
  username = StringField(validators = [InputRequired(), Length(min = 3, max = 25), unique_username], render_kw={"placeholder":"Username"})
  password = PasswordField(validators = [InputRequired(), Length(4, 15)], render_kw={"placeholder":"Password"})
  submit = SubmitField("Sign Up")
    
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
class Record_form(FlaskForm):
  problem_title = StringField(validators = [InputRequired(), Length(min=3, max=50)], render_kw={"placeholder":"Problem title"})
  problem_text = StringField(validators = [InputRequired()], render_kw={"placeholder":"Problem text"})
  # select problem type out of the given options
  problem_type = SelectField("Problem type", choices=[('Algebra','Algebra')])
  # write out the define step of the problem
  problem_define = StringField(validators = [InputRequired()], render_kw={"placeholder":"Step 1: define"})
  problem_encode = StringField(validators = [InputRequired()], render_kw={"placeholder":"Step 2: encode"})
  problem_solution = StringField(validators = [InputRequired()], render_kw={"placeholder":"Solution"})
  # choose folder from a list of already existing  ones
  old_folder = SelectField("Choose folder", choices=[])
  # or create a new folder
  new_folder = StringField(render_kw={"placeholder":"Or create a new folder"})
  
  # submit the form
  submit = SubmitField("Add problem")

  # problem titles have to be unique
  def validate_problem_title(self, problem_title):
    unique = Problem.query.filter_by(problem_title = problem_title.data).first()
    if unique != None:
      raise ValidationError("That problem title has already been taken.")

  # folder names have to be unique
  def validate_new_folder(self, folder_name):
    unique = Problem.query.filter_by(folder_name = folder_name.data).first()
    if unique != None:
      raise ValidationError("That folder name has already been taken.")

  # method to populate the StringField with folders that already exist for the user
  @classmethod
  def populate_folders(cls, user_id):
      if user_id:
          user_folders = Folder.query.filter_by(user_id=user_id).all()
          return [(folder.id, folder.name) for folder in user_folders]
      return []
