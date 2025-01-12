from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase
import requests
import os

config = {
    "apiKey": "AIzaSyBcE8jTyJuqH1gOncIPEHlrGLjE7geKuWU",
    "authDomain": "indv-project-d1395.firebaseapp.com",
    "projectId": "indv-project-d1395",
    "storageBucket": "indv-project-d1395.appspot.com",
    "messagingSenderId": "548095708664",
    "appId": "1:548095708664:web:afc97beb1472945279da0d",
    "measurementId": "G-Q2S0PEHTV8",
    "databaseURL": "https://indv-project-d1395-default-rtdb.europe-west1.firebasedatabase.app"}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'
UPLOAD_FOLDER = 'static/images/pets'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']


def spliting(filepath):
    img = str(filepath).split("'")[1]
    slash = "/"
    return f'{UPLOAD_FOLDER}{slash}{img}'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload_file(file):
    if request.method == 'POST':
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(UPLOAD_FOLDER + "/" + filename)

def get_img():
    URL = "https://dog.ceo/api/breeds/image/random"
    resp = requests.get(url = URL)
    resp = resp.text
    return resp.split('"')[3]

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']     
        try:
            login_session['user'] = auth.create_user_with_email_and_password(email, password)
            UID = login_session['user']['localId']
            user = {"username" : username,"email": email}
            db.child("Users").child(UID).set(user)
            return redirect(url_for('home'))
        except Exception as e:
            print(e)
    return render_template("signup.html", img=get_img())

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        try:
            UID = login_session['user']['localId']
            photo = request.files['dog_pic']
            upload_file(photo)
            print(photo)
            img_to_set = {"img": spliting(photo), "username":db.child("Users").child(UID).get().val()["username"]}
            print(img_to_set)
            db.child("Posts_uploaded").push(img_to_set)
            return redirect(url_for('upload'))
        except Exception as e:
            print(e)
            return redirect(url_for('error'))
    else:
        return render_template('publish_post.html', img=get_img())

@app.route('/error', methods=['GET', 'POST'])
def error():
    return render_template("error.html", img = get_img())

@app.route('/', methods=['GET', 'POST'])
def signin():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            login_session['user'] = auth.sign_in_with_email_and_password(email, password)
            return redirect(url_for('home'))
        except Exception as e:
            print(e)
    return render_template("signin.html", img=get_img())



@app.route('/home',  methods=['GET', 'POST'])
def home():
    UID = login_session['user']['localId']
    return render_template("home.html", username = db.child("Users").child(UID).get().val(), img=get_img())


@app.route('/signout')
def signout():
    login_session['user'] = None
    auth.current_user = None
    return redirect(url_for('signin'))

@app.route('/history')
def history():
    UID = login_session['user']['localId']
    return render_template("history.html", list = db.child("Photos").child(UID).get().val())



@app.route('/get_new_img',  methods=['GET', 'POST'])
def get_new_img():
    UID = login_session['user']['localId']
    img = get_img()
    img_to_set = {"img":img, "username":db.child("Users").child(UID).get().val()["username"]}
    if request.method == 'POST':
        db.child("Photos").child(UID).push(img_to_set)
        choice = request.form['yesOrNo'] 
        if choice == 'Yes': 
            db.child("Posts").push(img_to_set)
    return render_template("get_new_img.html", img=img)


@app.route('/show_posts',  methods=['GET', 'POST'])
def show_posts():
    return render_template("show_posts.html", list=db.child('Posts').get().val(), second_list=db.child('Posts_uploaded').get().val())


if __name__ == '__main__':
    app.run(debug=True)
 