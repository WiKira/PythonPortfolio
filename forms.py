from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreateProjectForm(FlaskForm):
    title = StringField("Project Title", validators=[DataRequired()])
    subtitle = StringField("Project Subtitle", validators=[DataRequired()])
    img_url = StringField("Image 1 URL", validators=[DataRequired(), URL()])
    description = CKEditorField("Description", validators=[DataRequired()])
    submit = SubmitField("Submit", render_kw={'class': 'button'})


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[Email(), DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), ])
    submit = SubmitField("Login", render_kw={'class': 'button'})


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[Email(), DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), ])
    submit = SubmitField("Login", render_kw={'class': 'button'})