import datetime

from flask import Flask, render_template


app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'


@app.route('/')
# TODO def show_all_mess():
def show_all_mess():
    return "200"


@app.route('/send_mess')
def send_mess(sender="", reciver="", mess="", subject=""):
    # TODO connect to db and send all info
    date = datetime.datetime.now()
    print(date)
    return str(date)


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
    app.run(debug=True)
