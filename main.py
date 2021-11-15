import datetime
import gunicorn
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
app.config['SQLALCHEMY_DATABASE_URI'] = 'https://data.heroku.com/datastores/fc60a22f-4c7a-481f-a3b8-28c2d020bef3'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(80), nullable=False)
    reciver = db.Column(db.String(80), nullable=False)
    mess = db.Column(db.String(80), nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    time = db.Column(db.String(80), nullable=False)


@app.route('/')
# TODO def show_all_mess():
def show_all_mess():
    a = Message.query.all()
    x = [n.mess for n in a]
    print(a)
    print(x)
    return str(x)


@app.route('/send_mess')
def send_mess():
    # TODO connect to db and send all info
    sender = request.form["sender"]
    receiver = request.form["receiver"]
    subject = request.form["subject"]
    mess = request.form['mess']
    date = datetime.datetime.now()
    print(date)
    message = Message(sender=sender, reciver=receiver, mess=mess, subject=subject, time=str(date))
    db.session.add(message)
    db.session.commit()
    return message.mess


@app.route('/show_all_unreaded_mess')
def show_all_unreaded_mess(sender, reciver, mess, subject, date):
    return "200"


@app.route('/read_mess')
def read_mess(sender, reciver, mess, subject, date):
    return "200"


@app.route('/delete_mess')
def delete_mess(sender, reciver, mess, subject, date):
    return


if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', debug=True)
