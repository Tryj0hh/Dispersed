'''App file that handles db creation and updating, app routes and POST/GET requests'''
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
db = SQLAlchemy(app)

class NewTrail(db.Model):
    '''db model. Delcares element names and types'''
    id = db.Column(db.Integer, primary_key=True)
    trailname = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.String(200), nullable=False)
    longitude = db.Column(db.String(200), nullable=False)
    date_traveled = db.Column(db.String(10), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
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
            date_traveled=date_traveled_input
        )

        try:
            db.session.add(new_trail)
            db.session.commit()
            return redirect('/')
        except:
            return 'These was a problem with your submission'


    else:
        trails = NewTrail.query.order_by(NewTrail.date_created).all()
        return render_template('index.html', trails = trails)


@app.route('/delete/<int:id>')
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
