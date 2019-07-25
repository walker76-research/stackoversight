from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField,TextAreaField

class AppInputForm():
    file = FileField('Upload pyhton file', validators = [FileAllowed(['py'])])
    submit = SubmitField('Upload')
