document.addEventListener('DOMContentLoaded', () => {
    
    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected, configure
    socket.on( 'connect', function() {
        
        // Configure form
        document.querySelector("#form").onsubmit = function () {
            const message = document.querySelector("#message").value;
            socket.emit('message', message, username);
            this.reset();
            return false;
        };

    });

    // Check for username
    var username = localStorage.getItem("username");

    // Prompt for username if no username in localStorage
    if (username == null) {
        username = prompt("Please enter your name", "Harry Potter");
        localStorage.setItem("username", username);
    }
    
    // Function to add new messages
    socket.on('message', function(message) {
        const li = document.createElement('li');
        li.innerHTML = message;
        const chat = document.querySelector("#chat");
        chat.append(li);
    });

});