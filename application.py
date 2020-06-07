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

# Default route
@app.route("/", methods=["GET"])
def index():
    msg_form = MessageForm()
    chan_form = ChannelForm()
    return render_template("index.html", form=msg_form, chan_form=chan_form, rooms=data["channels"])
        

# Channel create event
@socketio.on("chan create")
def createChannel(channel):
    if channel in data["channels"]:
        emit("error", message="Existing channel")

    else:
        data["channels"].append(channel)
        emit("new chan", channel, broadcast=True)


# Message event    
@socketio.on('message')
def handleMessage(msg, username, room):
    # If message has file in it
    if msg["has_file"] == 1:
        secure_name = secure_filename(msg['file']['name'])
        fqfn = f"{UPLOAD_FOLDER}//{secure_name}"
        # Write file to local system
        with open(fqfn, "w") as upload_file:
            print(msg["file"]["body"].decode('utf-8'))
            upload_file.write(msg["file"]["body"].decode('utf-8'))
        # Upload file to Amazon S3
        upload_s3_file(fqfn, S3_BUCKET, secure_name)
        s3_file = f"https://{S3_BUCKET}.s3.amazonaws.com/{secure_name}"
        # Remove file from local system
        os.remove(fqfn)
        message = {
            "message":f"{username}: {msg['message']}\n",
            "file_link": s3_file,
            "file_name": secure_name,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "return_file": 1
            }

    else:
        message = {
            "message":f"{username}: {msg['message']}\n",
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "return_file": 0
            }
    
    # Check if room already has messages in the server
    try:
        data["messages"][room]

    except KeyError:
        data["messages"][room] = []

    # Remove first message for saving only up to 100 messages
    if len(data["messages"][room]) == 100:
        messages.pop(0)

    # Save message history
    data["messages"][room].append(message)
    # Emit message to the server
    emit("message", message, room=room)


# Leave channel event
@socketio.on('leave')
def leave(username, room):
    # Leave channel message
    message = {
        "message":f"{username} has left the {room} room\n",
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "return_file": 0
        }

    emit("message", message, room=room)
    leave_room(room)


# Join channel event
@socketio.on('join')
def join(username, room):
    # Join channel message
    message = {
        "message":f"{username} has just joined this room. Say hello to {username}!\n",
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "return_file": 0
    }
    join_room(room)
    # Check if server has messages in this room
    try:
        messages = data["messages"][room]
    except KeyError:
        data["messages"][room] = []
        messages = data["messages"][room]
    emit("join", messages)
    emit("message", message, room=room)