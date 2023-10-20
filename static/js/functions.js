function deleteMessage(messageId) {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }
    request.open("DELETE", "/chat-message/" + messageId);
    request.send();
}

function likeMessage(messageId){
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }
    console.log(messageId)
    request.open("POST", "/chat-like");
    request.send(JSON.stringify({"messageId":messageId}));
    request.send();
}

function chatMessageHTML(messageJSON) {
    const username = messageJSON.username;
    const title = messageJSON.title;
    const likes = messageJSON.likes;
    const description = messageJSON.description;
    const messageId = messageJSON.id;
    let messageHTML =  
    `<div class=new_chat_message>
	<button onclick='deleteMessage(${messageId})'>❌</button>&nbsp;
	<span id='message_${messageId}'>${username}: <font size="+2"><b>${title}</b></font></span>
    </div>
    <div>
    <p>${description}</p>
	<button onclick='likeMessage(${messageId})'>💓&nbsp;(${likes})</button><br></br>
    </div>`
    return messageHTML;
}

function clearChat() {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML = "";
}

function addMessageToChat(messageJSON) {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML += chatMessageHTML(messageJSON);
    chatMessages.scrollIntoView(false);
    chatMessages.scrollTop = chatMessages.scrollHeight - chatMessages.clientHeight;
}

function sendChat() {
    const title_text_box = document.getElementById("title-text-box");
    const title = title_text_box.value;
    title_text_box.value = "";
    const description_text_box = document.getElementById("description-text-box");
    const description = description_text_box.value;
    description_text_box.value = "";
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }
    const messageJSON = {"title": title, "description": description};
    request.open("POST", "/chat-message");
    request.send(JSON.stringify(messageJSON));
    title_text_box.focus();
}

function updateChat() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearChat();
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addMessageToChat(message);
            }
        }
    }
    request.open("GET", "/chat-history");
    request.send();
}

function welcome() {
    document.addEventListener("keypress", function (event) {
        if (event.code === "Enter") {
            sendChat();
        }
    });

    document.getElementById("paragraph").innerHTML = "<br/>Welcome to the best chat system ever!!! Here you can chat and share images with other users 🤠";
    document.getElementById("chat-messages").focus();

    updateChat();
    setInterval(updateChat, 2000);
}
