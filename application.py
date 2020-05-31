import os

from flask import Flask, render_template, request, url_for
from flask_socketio import SocketIO, emit
from models.wtform_fields import MessageForm

# Configure app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

data = {
    "messages": [],
    "channels": []
}

@app.route("/")
def index():
    msg_form = MessageForm()
    return render_template("index.html", messages=data["messages"], form=msg_form)


@socketio.on('message')
def handleMessage(msg, username):
    message = f"{username}: {msg}"
    if len(data["messages"]) == 100:
        messages.pop(0)
    data["messages"].append(message)
    emit("message", message, broadcast=True)
