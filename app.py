'''App file that handles db creation and updating, app routes and POST/GET requests'''
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
db = SQLAlchemy(app)

class NewTrail(db.Model):
    '''db model. Declares element names and types'''
    id = db.Column(db.Integer, primary_key=True)
    trailname = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.String(200), nullable=False)
    longitude = db.Column(db.String(200), nullable=False)
    date_traveled = db.Column(db.String(10), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    trails = db.relationship('NewTrail', backref='author', lazy=True)

    def __repr__(self):
        return '<Task %r>' % self.id
    
'''with app.app_context():
    db.create_all()'''



bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if not username or not email or not password:
            flash('All fields are required!')
            return redirect('/register')
        
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(username=username, email=email, password=hashed_pw)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration Successful! You can now login.')
            return redirect('/login')
        except:
            flash('Those credentials cannot be used.')
            return redirect('/register')
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Log in successful.')
            return redirect('/')
        else:
            flash('Invalid Credentials. Try again.')
            return redirect('/login')
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out.')
    return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    if request.method == 'POST':
        trail_name_input = request.form['trailname'].strip()
        latitude_input = request.form['latitude'].strip()
        longitude_input = request.form['longitude'].strip()
        date_traveled_input = request.form['date_traveled'].strip()

        if not trail_name_input or not latitude_input or not longitude_input or not date_traveled_input:
            flash('All fields are required!')
            return redirect('/')


        new_trail = NewTrail(
            trailname=trail_name_input,
            latitude=latitude_input,
            longitude=longitude_input,
            date_traveled=date_traveled_input,
            author=current_user
        )

        try:
            db.session.add(new_trail)
            db.session.commit()
            return redirect('/')
        except:
            return 'These was a problem with your submission'


    else:
        trails = NewTrail.query.filter_by(user_id=current_user.id).order_by(NewTrail.date_created).all()
        return render_template('index.html', trails = trails)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    trail_to_delete = NewTrail.query.get_or_404(id)

    try:
        db.session.delete(trail_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        flash('There was a problem deleting this trail')
        return redirect('/')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    trails = NewTrail.query.get_or_404(id)

    if request.method == 'POST':
        trails.trailname = request.form['trailname'].strip()
        trails.latitude = request.form['latitude'].strip()
        trails.longitude = request.form['longitude'].strip()
        trails.date_traveled = request.form['date_traveled'].strip()
        try:
            db.session.commit()
            return redirect('/')
        except:
            flash('There was a problem updating this trail')
            return redirect('/')

    else:
        return render_template('update.html', trails = trails)






if __name__ == "__main__":
    app.run(debug = True)
