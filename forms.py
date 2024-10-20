from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from models import User
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