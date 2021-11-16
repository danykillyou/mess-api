import datetime
import gunicorn
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://awakmsnbccrbfy:f3b3e4e1d86f1a2722f8011507c6ce84af6da8d812e6c7537266f32236401cb4@ec2-54-216-185-51.eu-west-1.compute.amazonaws.com:5432/dar0ufs7rl9a5h'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(80), nullable=False)
    receiver = db.Column(db.String(80), nullable=False)
    mess = db.Column(db.String(80), nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    time = db.Column(db.String(80), nullable=False)
    is_read = db.Column(db.Boolean)

    def print_all(self):
        return {"id": self.id, "sender": self.sender, "receiver": self.receiver, "mess": self.mess,
                "subject": self.subject, "time": self.time, "is_read": self.is_read}

    def read(self):
        self.is_read = True
        db.session.commit()


@app.route('/')
# TODO def show_all_mess():
def show_all_mess():
    sender = request.form["sender"]
    all = Message.query.filter(Message.receiver == sender).all()
    x = []
    for mess in all:
        mess.read()
        x.append(mess.print_all())
    # x = [mess.is_read==True , for mess in all]
    # print(a)
    # print(x)
    return str(x)


@app.route('/send_mess')
def send_mess():
    # TODO connect to db and send all info
    sender = request.form["sender"]
    receiver = request.form["receiver"]
    subject = request.form["subject"]
    mess = request.form['mess']
    date = datetime.datetime.now()
    # print(str(date))
    message = Message(sender=sender, receiver=receiver, mess=mess, subject=subject, time=str(date), is_read=False)
    db.session.add(message)
    db.session.commit()
    return message.mess


@app.route('/show_all_unreaded_mess')
def show_all_unreaded_mess():
    x=[]
    sender = request.form["sender"]
    all = Message.query.filter(Message.is_read == False).filter( Message.receiver == sender)
    print(all)
    x = [mess.print_all() for mess in all]
    return str(x)


@app.route('/read_mess')
def read_mess(sender, reciver, mess, subject, date):
    return "200"


@app.route('/delete_mess')
def delete_mess():
    Message.__table__.drop(db.engine)
    return "ok"


if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', debug=True)
