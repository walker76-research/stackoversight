from flask import Flask, render_template, url_for,redirect,flash,request
from werkzeug.utils import secure_filename

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField,TextAreaField
from wtforms.validators import ValidationError
from os.path import dirname

class AppInputForm(FlaskForm):
	file = FileField('Choose file', validators = [FileAllowed(['py'])]) #java
	submit = SubmitField('Upload')



import os
app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
UPLOAD_FOLDER = dirname(__file__) + '/Uploadedfiles'
ALLOWED_EXTENSIONS = {'py'} #java

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
current_file = ''


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def readfile(filename):
	path =UPLOAD_FOLDER +'/'+ filename
	with open(path, 'r') as content_file:
		content = content_file.read()
	return content


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/app',methods=['GET','POST'])
def application():
	form = AppInputForm()
	global current_file
	
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file part')
			return redirect(url_for('application'))
		file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
		if file.filename == '':
			#flash('No selected file','success')
			return render_template('app.html',form=form,error='NoSelectedFile')
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			current_file = file.filename
			return redirect(url_for('upload_success',
                                    filename=filename))
		else:
			#flash('incorrect file')
			
			return render_template('app.html',form=form,error='IncorrectFileType')
	return render_template('app.html',form=form,error='')


@app.route('/editor', methods=['GET','POST'])
def editor():
	return render_template('editor.html')

@app.route('/app/upload_sucess')
def upload_success():
	return render_template('upload_success.html')

@app.route('/result', methods=['GET','POST'])
def result():
	# here will be passed the output of search 
	#file_output =
	file_input = readfile(current_file)
	return render_template('result.html', file_input=file_input)# ,file_out = file_output)

if __name__ == '__main__':
	app.run()

