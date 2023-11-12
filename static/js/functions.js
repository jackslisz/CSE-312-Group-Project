const ws = true;
let socket = null;

function initWS() {
    // Establish a WebSocket connection with the server
    socket = new WebSocket('ws://' + window.location.host + '/websocket');

    // Called whenever data is received from the server over the WebSocket connection
    socket.onmessage = function (ws_message) {
        const message = JSON.parse(ws_message.data);
        const messageType = message.messageType
        if(messageType === 'chatMessage'){
            addMessageToChat(message);
        } else {
            // send message to WebRTC
            processMessageAsWebRTC(message, messageType);
        }
    }
}


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
    // request.send();
}

function chatMessageHTML(messageJSON) {
    // console.log(document.getElementById("formfile").files[0]);
    // console.log(messageJSON);
    const username = messageJSON.username;
    const title = messageJSON.title;
    const likes = messageJSON.likes;
    const description = messageJSON.description;
    const messageId = messageJSON.id;
    const choice1 = messageJSON.choice1;
    const choice2 = messageJSON.choice2;
    const choice3 = messageJSON.choice3;
    const choice4 = messageJSON.choice4;
    // const image = null;
    
    const image = 'quizicon.ico';
    let messageHTML =  
    `<div class=new_chat_message>
	<i class="bi bi-person-fill"></i>
    <span id='message_${messageId}'>${username}<br><br></span>
    <img src="/static/img/${image}"></br></br>
    <font size="+2"><b>${title}</b></font>
    <br>
    <a><b>${description}<b></a>
    <hr style="border: 1px dotted #ffffff;">
    </div>
    <div>
    <form onsubmit="submitAnswer()" method="post">
    <label>
        1:
        <input id="Choice 1" type="radio" name="choices">
    </label>
    <label>
        ${choice1}
    </label>
    <br>
    <label>
        2:
        <input id="Choice 2" type="radio" name="choices">
    </label>
    <label>
        ${choice2}
    </label>
    <br>
    <label>
        3:
        <input id="Choice 3" type="radio" name="choices">
    </label>
    <label>
        ${choice3}
    </label>
    <br>
    <label>
        4:
        <input id="Choice 4" type="radio" name="choices">
    </label>
    <label>
        ${choice4}
    </label>
    <br>
    <input type="submit" value="Submit">
    </form>
    <br>
    </div>`
    if (document.getElementById("formfile").files[0] != undefined) {
        const image = document.getElementById("formfile").files[0].name;
        messageHTML = messageHTML.replace(`<hr style=\"border: 1px dotted #ffffff;\">`,`<br><img src=\"static/img/${image}\"></img><hr style=\"border: 1px dotted #ffffff;\">`);
        console.log(messageHTML);
    }

    // THE FOLLOWING 2 LINES WERE REMOVED FROM AFTER LINE 105
    // <button onclick='deleteMessage(${messageId})'>❌</button>&nbsp;
	// <button onclick='likeMessage(${messageId})'>💓&nbsp;(${likes})</button><br></br>

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

function submitAnswer() {
    console.log("submitanswercheck")
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }
    var options = document.getElementsByName('choice');
    var selected;
    for(var i = 0; i < options.length; i++){
        if(options[i].checked){
            selected = options[i].value;
        }
    }
    const correct_answer = document.getElementById("right-option");
    const correct_answer_value = correct_answer.options[correct_answer.selectedIndex].text;
    console.log("compfngwku4g check")
    const messageJSON = {"selected": selected, "correctornot": selected == correct_answer_value};
    if(ws){
        console.log("websocketreceptioncheck")
        socket.send(JSON.stringify({'messageType': 'questionAnswer',"selected": selected, "correctornot": selected == correct_answer_value}));
        console.log("postjkeb v")
    }
    else{
        request.open("POST", "/submit-answer");
        request.send(JSON.stringify(messageJSON));
    }
}


function sendChat() {
    const title_text_box = document.getElementById("title-text-box");
    const title = title_text_box.value;
    title_text_box.value = "";
    const description_text_box = document.getElementById("description-text-box");
    const description = description_text_box.value;
    description_text_box.value = "";
    const choice1_text_box = document.getElementById("choice-1-text");
    const choice1 = choice1_text_box.value;
    choice1_text_box.value = "";
    const choice2_text_box = document.getElementById("choice-2-text");
    const choice2 = choice2_text_box.value;
    choice2_text_box.value = "";
    const choice3_text_box = document.getElementById("choice-3-text");
    const choice3 = choice3_text_box.value;
    choice3_text_box.value = "";
    const choice4_text_box = document.getElementById("choice-4-text");
    const choice4 = choice4_text_box.value;
    choice4_text_box.value = "";
    const correct_answer = document.getElementById("right-option");
    const correct_answer_value = correct_answer.options[correct_answer.selectedIndex].text;
    correct_answer.value = "choice-1";
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }
    const messageJSON = {"title": title, "description": description, "choice1": choice1, "choice2": choice2, "choice3": choice3, "choice4": choice4, "correctanswer": correct_answer_value};
    request.open("POST", "/chat-message");
    if(ws){
        socket.send(JSON.stringify({'messageType': 'chatMessage',"title": title, "description": description,"choice1": choice1, "choice2": choice2, "choice3": choice3, "choice4": choice4, "correctanswer": correct_answer_value}));
    }
    else{
        request.send(JSON.stringify(messageJSON));
        title_text_box.focus();
    }

    // request.send(JSON.stringify(messageJSON));
    // title_text_box.focus();

    //     if (ws) {
    //     // Using WebSockets
    //     socket.send(JSON.stringify({'messageType': 'chatMessage', 'message': message}));
    // } else {
    //     // Using AJAX
    //     const request = new XMLHttpRequest();
    //     request.onreadystatechange = function () {
    //         if (this.readyState === 4 && this.status === 200) {
    //             console.log(this.response);
    //         }
    //     }
    //     const messageJSON = {"message": message};
    //     request.open("POST", "/chat-message");
    //     request.send(JSON.stringify(messageJSON));
    // }
    // chatTextBox.focus();
}

function updateChat() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            // clearChat();
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

    document.getElementById("paragraph").innerHTML = "<center>Post and answer questions using the form below! Do you have what it takes to be the ultimate QUIZMASTER??? 🤔</center>";
    document.getElementById("chat-messages").focus();

    updateChat();

    if (ws) {
        initWS();
    } else {
        setInterval(updateChat, 2000);
        const videoElem = document.getElementsByClassName('video-chat')[0];
        videoElem.parentElement.removeChild(videoElem);
        setInterval(updateChat, 2000);
    }

}