from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'


@app.route('/')
# TODO def show_all_mess():
def show_all_mess():
    return


@app.route('/send_mess')
def send_mess(sender, reciver, mess, subject, date):
    # TODO connect to db and send all info
    return


@app.route('/show_all_unreaded_mess')
def send_mess(sender, reciver, mess, subject, date):
    return


@app.route('/read_mess')
def send_mess(sender, reciver, mess, subject, date):
    return


@app.route('/delete_mess')
def send_mess(sender, reciver, mess, subject, date):
    return


def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')


if __name__ == '__main__':
    app.run(debug=True)
