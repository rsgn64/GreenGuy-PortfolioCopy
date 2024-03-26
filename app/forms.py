from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired
import sqlalchemy as sa
from app import db
from app.models import BlogPost

class AddBlogPostForm(FlaskForm):
    #Form to add a new blog post via a zip file with defined structure.
    #The actual post Title and Description will be extracted from the uploaded file.
    post_name = StringField('Post Name (for URL)', validators=[DataRequired()])
    post_zip_file = FileField('Zip File', validators=[FileRequired()])
    submit = SubmitField('Add Post')

    #Validate that I don't accidentally make two posts with same name in DB
    #Won't be validating secure filename as I will be the only one uploading and it will be password-locked.
    def validate_post_name(self, post_name):
        post = db.session.scalar(sa.select(BlogPost).where(BlogPost.post_name == post_name.data))
        if post is not None:
            raise ValidationError('A blog post with that Post Name already exists. Please choose a different name.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')
