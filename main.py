import datetime
import gunicorn
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgresql://awakmsnbccrbfy:f3b3e4e1d86f1a2722f8011507c6ce84af6da8d812e6c7537266f32236401cb4@ec2-54-216-185-51.eu-west-1.compute.amazonaws.com:5432/dar0ufs7rl9a5h'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(80), nullable=False)
    receiver = db.Column(db.String(80), nullable=False)
    mess = db.Column(db.String(80), nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    time = db.Column(db.String(80), nullable=False)
    receiver_status = db.Column(db.String(80), nullable=False)  # deleted,read,unread
    sender_status = db.Column(db.String(80), nullable=False)  # sent,deleted

    def print_all(self):
        return {"id": self.id, "sender": self.sender, "receiver": self.receiver,
                "subject": self.subject, "time": self.time, "sender_status": self.sender_status,
                "receiver_status": self.receiver_status}


@app.route('/')
# TODO def show_all_mess():
def show_all_mess():
    sender = request.form["sender"]
    all_inbox = Message.query.filter(and_(Message.receiver == sender, Message.receiver_status != "deleted")).all()
    all_outbox = Message.query.filter(and_(Message.sender == sender, Message.sender_status != "deleted")).all()
    x = [mess.print_all() for mess in all_inbox]
    y = [mess.print_all() for mess in all_outbox]

    # x = [mess.is_read==True , for mess in all]
    # print(a)
    # print(x)
    return {"inbox": x, "outbox": y}


@app.route('/send_mess')
def send_mess():
    # TODO connect to db and send all info
    sender = request.form["sender"]
    receiver = request.form["receiver"]
    subject = request.form["subject"]
    mess = request.form["mess"]
    date = datetime.datetime.now()
    # print(str(date))
    message = Message(sender=sender, receiver=receiver, mess=mess, subject=subject, time=str(date),
                      receiver_status="unread", sender_status="sent")
    db.session.add(message)
    db.session.commit()
    return message.mess


@app.route('/show_all_unreaded_mess')
def show_all_unreaded_mess():
    sender = request.form["sender"]
    all = Message.query.filter(Message.receiver == sender).filter(Message.receiver_status == "unread").filter()
    print(all)
    x = [mess.print_all() for mess in all]
    return str(x)


@app.route('/read_mess')
def read_mess():
    sender = request.form["sender"]
    mess_id = request.form["id"]
    mess = Message.query.filter(
        and_(Message.id == mess_id, Message.sender == sender, Message.sender_status != "deleted")).first()
    if mess is None:
        mess = Message.query.filter(
            and_(Message.id == mess_id, Message.receiver == sender, Message.receiver_status != "deleted")).first()

        if mess is not None:
            mess.receiver_status = "read"
            db.session.commit()
            return mess.mess
    else:
        return mess.mess
    return "no message"


@app.route('/delete_db')
def delete_db():
    Message.__table__.drop(db.engine)
    return "ok"


@app.route('/delete_mess')
def delete_mess():
    sender = request.form["sender"]
    mess_id = request.form["id"]
    mess = Message.query.filter(
        and_(Message.id == mess_id, Message.sender == sender, Message.sender_status != "deleted")).first()
    if mess is None:
        mess = Message.query.filter(
            and_(Message.id == mess_id, Message.receiver == sender, Message.receiver_status != "deleted")).first()

        if mess is not None:
            mess.receiver_status = "deleted"
            db.session.commit()
            return mess.mess
    else:
        mess.sender_status = "deleted"
        db.session.commit()

        return mess.mess
    return "cant delete message"


if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', debug=True)
