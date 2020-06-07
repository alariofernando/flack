import os
from datetime import datetime

from helpers import upload_s3_file

from flask import Flask, render_template, request, url_for, redirect
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, emit, leave_room, join_room
from models.wtform_fields import MessageForm, ChannelForm

# S3 Bucket info
UPLOAD_FOLDER = r'C:\Users\lockh\newCode\pythonProjects\project2\project2\uploads'
S3_BUCKET = "alferpir-flack-project"

# Configure app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
socketio = SocketIO(app)

# Server side memory data
data = {
    "messages": {"Main":[],},
    "channels": ["Main"]
}

# 
@app.route("/", methods=["GET"])
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
    if msg["has_file"] == 1:
        secure_name = secure_filename(msg['file']['name'])
        fqfn = f"{UPLOAD_FOLDER}//{secure_name}"
        with open(fqfn, "w") as upload_file:
            print(msg["file"]["body"].decode('utf-8'))
            upload_file.write(msg["file"]["body"].decode('utf-8'))
        upload_s3_file(fqfn, S3_BUCKET, secure_name)
        s3_file = f"https://{S3_BUCKET}.s3.amazonaws.com/{secure_name}"
        os.remove(fqfn)
        message = {
            "message":f"{username}: {msg['message']}",
            "file_link": s3_file,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "return_file": 1
            }
    else:
        message = {
            "message":f"{username}: {msg['message']}",
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "return_file": 0
            }
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
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "return_file": 0
        }
    emit("message", message, room=room)
    leave_room(room)

@socketio.on('join')
def join(username, room):
    message = {
        "message":f"{username} has just joined this room. Say hello to {username}!",
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "return_file": 0
    }
    join_room(room)
    try:
        messages = data["messages"][room]
    except KeyError:
        data["messages"][room] = []
        messages = data["messages"][room]
    emit("join", messages)
    emit("message", message, room=room)