import sqlalchemy
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_, DateTime
import hashlib, datetime, gunicorn, uuid


salt = b'\x15\\\xcd\x1c\xef\xbf8\xfb\xd542uG\xb2\xdd\xb8\xdcE`\xcd\x91\x93*R\x8c\xeaXb\xcc\x86\x9e\xe7'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgresql://awakmsnbccrbfy:f3b3e4e1d86f1a2722f8011507c6ce84af6da8d812e6c7537266f32236401cb4@ec2-54-216-185-51.eu-west-1.compute.amazonaws.com:5432/dar0ufs7rl9a5h'
db = SQLAlchemy(app)


def check_authentication(mess_id, id):
    user = User.query.filter(User.id == id).first()
    # if user authenticated. this check guaranties that every user can change only his messages (prevent hacker attack)
    if not user: return None
    mess_receiver = Message.query.filter(
        and_(Message.id == mess_id, Message.receiver == user.email, Message.receiver_status != "deleted")).first()
    mess_sender = Message.query.filter(
        and_(Message.id == mess_id, Message.sender == user.email, Message.sender_status != "deleted")).first()
    # if there are no found messages return None
    if not mess_sender and not mess_receiver: return None
    return {"sender": mess_sender, "receiver": mess_receiver}
    # check if message is received by current user. if true change receiver_status to read and return it

    # if mess:
    #     mess.receiver_status = "read"
    #     db.session.commit()
    #     return mess


class User(db.Model):
    id = db.Column(db.String(120), primary_key=True)
    password = db.Column(db.LargeBinary(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def print_all(self):
        return {"id": self.id, "email": self.email, "password": self.password}


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(80), nullable=False)
    receiver = db.Column(db.String(80), nullable=False)
    mess = db.Column(db.String(80), nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    time = db.Column(DateTime, nullable=False)
    receiver_status = db.Column(db.String(80), nullable=False)  # deleted,read,unread
    sender_status = db.Column(db.String(80), nullable=False)  # sent,deleted
    sender_id = db.Column(db.String(80), nullable=False)

    def print_all(self):
        return {"id": self.id, "sender": self.sender, "receiver": self.receiver,
                "subject": self.subject, "time": self.time, "sender_status": self.sender_status,
                "receiver_status": self.receiver_status}


@app.route("/signup",methods=["POST"])
def signup():
    try:
        password = request.form["password"]
        email = request.form["email"]
        key = hashlib.pbkdf2_hmac('sha256',  # The hash digest algorithm for HMAC
                                  password=password.encode('utf-8'),  # Convert the password to bytes
                                  salt=salt,  # Randomly generated sequence for security
                                  iterations=100000, )  # It is recommended to use at least 100,000 iterations of SHA-256
        # I used GUID as token instead of email or simple id order, for high security level
        user = User(id=str(uuid.uuid4()), password=key, email=email)
        print(key)
        # Add new user to DataBase table
        db.session.add(user)
        db.session.commit()
        return user.email + "\n now you can sign in"
    except sqlalchemy.exc.IntegrityError as e:
        return str(e.args).replace(' Key','').replace('(','').replace(')','').split(r"\n")[1]
    except Exception as e:
        return str(e.args)


@app.route("/signin")
def signin():
    password = request.form["password"]
    email = request.form["email"]
    # Check if user exist in DataBase
    user = User.query.filter(User.email == email).first()
    if user is None: return "email or password is wrong"
    key = hashlib.pbkdf2_hmac('sha256', password=password.encode('utf-8'), salt=salt, iterations=100000)
    print(str(key) + "\n"
          + str(user.password))
    # Generate new hashed password with the provided password and
    # compere it with the one store in the DataBase
    # If the passwords match return to the user his id
    if user.password == key:
        return str(user.id)
    return "email or password is wrong"


@app.route('/get_all_mess')
# TODO exception for all errors
def get_all_mess():
    try:
        id = request.form["id"]
        user = User.query.filter(User.id == id).first()
        if not user: return {"data": "your token is not valid"}
        my_email = user.email
        all_outbox = Message.query.filter(and_(Message.sender == my_email, Message.sender_status != "deleted")).all()
        all_inbox = Message.query.filter(and_(Message.receiver == my_email, Message.receiver_status != "deleted")).all()
        inbox = [mess.print_all() for mess in all_inbox]
        outbox = [mess.print_all() for mess in all_outbox]
        return {"inbox": inbox, "outbox": outbox}
    except Exception as e:
        return str(e.args)


@app.route('/send_mess',methods=["POST"])
def send_mess():
    try:
        id = request.form["id"]
        receiver = request.form["receiver"]
        subject = request.form["subject"]
        mess = request.form["mess"]
        time = datetime.datetime.now()
        user = User.query.filter(User.id == id).first()
        sender = user.email
        message = Message(sender=sender, receiver=receiver, mess=mess, subject=subject, time=time,
                          receiver_status="unread", sender_status="sent",sender_id=id )
        # Add new message to DataBase table
        db.session.add(message)
        db.session.commit()
        return message.mess
    except Exception as e:
        return str(e.args)


@app.route('/show_all_unreaded_mess')
def show_all_unreaded_mess():
    try:
        id = request.form["id"]
        user = User.query.filter(User.id == id).first()
        if not user: return {"data": "your token is not valid"}
        my_email = user.email
        all = Message.query.filter(and_(Message.receiver == my_email, Message.receiver_status == "unread")).all()
        print(all)
        x = [mess.print_all() for mess in all]
        return {"inbox (unread)": x}
    except Exception as e:
        return str(e.args)


@app.route('/read_mess')
def read_mess():
    try:
        messes = check_authentication(request.form["mess_id"], request.form["id"])
        if not messes: return {"data": "your token is not valid or you don't have the authorization to this request"}
        if messes["receiver"]:
            messes["receiver"].receiver_status = "read"
            db.session.commit()
            return messes["receiver"].mess
        elif messes["sender"]:
            return messes["sender"]
        return "no message"
    except Exception as e:
        return str(e.args)


@app.route('/delete_db')
def delete_db():
    Message.__table__.drop(db.engine)
    return "ok"


@app.route('/delete_mess',methods=["POST"])
def delete_mess():
    try:
        messes = check_authentication(request.form["mess_id"], request.form["id"])
        if not messes: return {"data": "your token is not valid or you don't have the authorization to this request"}
        print(f"{messes}   messes")
        if messes["receiver"]:
            messes["receiver"].receiver_status = "deleted"
        if messes["sender"]:
            messes["sender"].sender_status = "deleted"
        db.session.commit()
        return {"data": "message deleted"}
    except Exception as e:
        return str(e.args)
    # # check if message is sent by current user. if true delete it
    # mess_sender = Message.query.filter(and_(Message.id == mess_id, Message.sender_id == id)).first()
    # if mess_sender:
    #     mess_sender.sender_status = "deleted"
    #     db.session.commit()
    # # check if message is received by current user. if true delete it
    # mess_receiver = Message.query.filter(and_(Message.id == mess_id, Message.receiver == user.email)).first()
    # if mess_receiver:
    #     mess_receiver.receiver_status = "deleted"
    #     db.session.commit()
    # return


if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', debug=True)
