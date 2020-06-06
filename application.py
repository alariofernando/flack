import os
from datetime import datetime

from flask import Flask, render_template, request, url_for, redirect
from flask_socketio import SocketIO, emit, leave_room, join_room
from models.wtform_fields import MessageForm, ChannelForm

# Configure app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

data = {
    "messages": {"Main":[],},
    "channels": ["Main"]
}

@app.route("/")
def index():
    msg_form = MessageForm()
    chan_form = ChannelForm()
    return render_template("index.html", form=msg_form, chan_form=chan_form, rooms=data["channels"])


@socketio.on("chan create")
def createChannel(channel):
    if channel in data["channels"]:
        emit("error", message="Existing channel")
    else:
        data["channels"].append(channel)
        emit("new chan", channel, broadcast=True)
    
@socketio.on('message')
def handleMessage(msg, username, room):
    message = {
        "message":f"{username}: {msg}",
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
    try:
        data["messages"][room]
    except KeyError:
        data["messages"][room] = []
    if len(data["messages"][room]) == 100:
        messages.pop(0)
    data["messages"][room].append(message)
    emit("message", message, room=room)

@socketio.on('leave')
def leave(username, room):
    message = {
        "message":f"{username} has left the room",
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
    emit("message", message, room=room)
    leave_room(room)

@socketio.on('join')
def join(username, room):
    message = {
        "message":f"{username} has just joined this room. Say hello to {username}!",
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    join_room(room)
    try:
        messages = data["messages"][room]
    except KeyError:
        data["messages"][room] = []
        messages = data["messages"][room]
    emit("join", messages)
    emit("message", message, room=room)