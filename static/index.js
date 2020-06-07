document.addEventListener('DOMContentLoaded', () => {
    
    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected, configure
    socket.on( 'connect', function() {
        
        // Configure form
        document.querySelector("#form").onsubmit = function () {
            const message = this.querySelector("#message").value;
            const fileField = this.querySelector("#file");
            if (fileField.files.length) {
                const file = {"body":fileField.files[0], "name": fileField.files[0].name}
                var data = { "message": message, "has_file": 1, "file": file};
            } else {
                var data = { "message": message, "has_file": 0 };
            }
            socket.emit('message', data, username, room);
            this.reset();
            return false;
        };

        // Configure channel creation
        document.querySelector('#create-channel').onclick = () => {
            document.querySelector("#main-chat").style.display = "none";
            document.querySelector("#chan-form").style.display = "block";
            return false;
        };

        // Configure channel creation form
        document.querySelector("#chan-form").onsubmit = function () {
            const chanName = document.querySelector("#channel-name").value;
            socket.emit("chan create", chanName);
            document.querySelector("#main-chat").style.display = "block";
            document.querySelector("#chan-form").style.display = "none";
            document.querySelector("#channel-name").value = "";
            return false;
        }

        // Configure rooms
        document.querySelectorAll(".chat-room").forEach(data => {
            data.onclick = () => {
                let newRoom = data.innerHTML;
                if (newRoom == room) {
                    msg = `You're already at ${room}`;
                    alert(msg);
                } else {
                    // Leave room and join NewRoom
                    socket.emit('leave', username, room);
                    room = newRoom;
                    localStorage.setItem("room", room)
                    document.querySelector("#chat").innerHTML = "";
                    socket.emit('join', username, room);
                }
            }
        });

    });

    // Check for username
    var username = localStorage.getItem("username");

    // Prompt for username if no username in localStorage
    if (username == null) {
        username = prompt("Please enter your name", "Harry Potter");
        localStorage.setItem("username", username);
    }

    // Set username in the page
    document.querySelector("#user-field").innerHTML = "Username: " + username;
    
    // Check for last room
    let room = localStorage.getItem("room");

    // Prompt for room if no last room in localStorage
    if (room == null) {
        room = "Main";
        localStorage.setItem("room", room);
        socket.emit('join', username, room);
    } else {
        localStorage.setItem("room", room);
        socket.emit('join', username, room);
    }

    document.querySelector("#room-field").innerHTML = "Room: " + room;


    // Function to add new messages
    socket.on('message', function(message) {
        const li = document.createElement('li');
        const small = document.createElement('small');
        const br = document.createElement('br');
        small.innerHTML = message['timestamp'];
        li.innerHTML = message['message'];
        if (message["return_file"] == 1) {
            var aLink = document.createElement('a');
            aLink.href = message["file_link"];
            aLink.innerHTML = message["file_name"];
            li.append(document.createElement('br'));
            li.append(aLink);
        }
        li.append(br);
        li.append(small);
        const chat = document.querySelector("#chat");
        chat.append(li);
    });

    // Event to populate chat with already existing messages
    socket.on('join', messages => {
        messages.forEach( item => {
            const li = document.createElement('li');
            const small = document.createElement('small');
            const br = document.createElement('br');
            small.innerHTML = item['timestamp'];
            li.innerHTML = item['message'];
            if (item["return_file"] == 1) {
                var aLink = document.createElement('a');
                aLink.href = item["file_link"];
                aLink.innerHTML = item["file_name"];
                li.append(document.createElement('br'));
                li.append(aLink);
            }
            li.append(br);
            li.append(small);
            document.querySelector('#chat').append(li);
        });
    });

    // Event for listening to errors
    socket.on('error', message => {
        alert(message);
    });

    // Event to add new channel to the list on creation
    socket.on('new chan', chanName => {
        const li = document.createElement('li');
        li.innerHTML = chanName;
        li.classList.add("chat-room");
        li.onclick = function () {
            let newRoom = this.innerHTML;
            if (newRoom == room) {
                msg = `You're already at ${room}`;
                alert(msg);
            } else {
                // Leave room and join NewRoom
                socket.emit('leave', username, room);
                room = newRoom;
                localStorage.setItem("room", room)
                document.querySelector("#chat").innerHTML = "";
                document.querySelector("#room-field").innerHTML = "Room: " + room;
                socket.emit('join', username, room);
            }
        }

        document.querySelector('#room-list').append(li);
    });

});
