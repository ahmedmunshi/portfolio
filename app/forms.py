from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import Category
from app import db

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class PhotoUploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    categories = SelectMultipleField('Categories', coerce=int)
    featured = BooleanField('Feature on Homepage')
    photo = FileField('Photo', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Upload')
    
    def __init__(self, *args, **kwargs):
        super(PhotoUploadForm, self).__init__(*args, **kwargs)
        self.categories.choices = [(c.id, c.name) for c in Category.query.order_by('name')]

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=64)])
    submit = SubmitField('Add Category')
    
    def validate_name(self, name):
        category = Category.query.filter_by(name=name.data).first()
        if category is not None:
            raise ValidationError('Category already exists.') 