const ws = true;
let socket = null;
let timers = {};
let timerInterval;


function initWS() {
    // Establish a WebSocket connection with the server
    socket = new WebSocket('wss://' + window.location.host + '/websocket');

    // Called whenever data is received from the server over the WebSocket connection
    socket.onmessage = function (ws_message) {
        var socket = io();
        socket.on('connect', function() {
            socket.emit('websocket_message', {data: 'I\'m connected!'});
        });
        const message = JSON.parse(ws_message.data);
        const messageType = message.messageType
        if(messageType === 'chatMessage'){
            addMessageToChat(message);
        } else {
            // send message to WebRTC
            //processMessageAsWebRTC(message, messageType);
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
}


function chatMessageHTML(messageJSON) {
    const username = messageJSON.username;
    const title = messageJSON.title;
    const likes = messageJSON.likes;
    const description = messageJSON.description;
    const messageId = messageJSON.id;
    const choice1 = messageJSON.choice1;
    const choice2 = messageJSON.choice2;
    const choice3 = messageJSON.choice3;
    const choice4 = messageJSON.choice4;
    const img = messageJSON.image;
    const question_ = title.toString();

    let messageHTML =  
    `<div class=new_chat_message>
	<i class="bi bi-person-fill"></i>
    <span id='message_${messageId}'>${username}<br><br></span>
    <img src="${img}" id="img" width="100" height="100"></br>
    <font size="+2"><b>${title}</b></font>
    <br>
    <a><b>${description}<b></a>
    <hr style="border: 1px dotted #ffffff;">
    </div>
    <div id="timer_${messageId}"></div>
    <form onsubmit="submitAnswer(event, ${messageId},'${question_}','${username}')" method="post">
    <div>
    
    <label>
        1:
        <input id="Choice 1" type="radio" name="${messageId}">
    </label>
    <label>
        ${choice1}
    </label>
    <br>
    <label>
        2:
        <input id="Choice 2" type="radio" name="${messageId}">
    </label>
    <label>
        ${choice2}
    </label>
    <br>
    <label>
        3:
        <input id="Choice 3" type="radio" name="${messageId}">
    </label>
    <label>
        ${choice3}
    </label>
    <br>
    <label>
        4:
        <input id="Choice 4" type="radio" name="${messageId}">
    </label>
    <label>
        ${choice4}
    </label>
    <br>
    <input type="submit" id="submit_${messageId}" value="Submit">
    </form>
    <button onclick="startTimer(${messageId})">Start Timer</button>
    <br>
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

function startTimer(messageId) {
        timers[messageId] = {
        timeRemaining: 60,
        interval: setInterval(function () {
            if (timers[messageId].timeRemaining > 0) {
                timers[messageId].timeRemaining--;
                updateTimerDisplay(messageId);
            } else {
                disableSubmitButton(messageId);
                clearInterval(timers[messageId].interval);
            }
        }, 1000),
    };

    updateTimerDisplay(messageId);
}

function updateTimerDisplay(messageId) {
    const timerElement = document.getElementById(`timer_${messageId}`);
    if (timerElement) {
        if (timers[messageId].timeRemaining > 0) {
            timerElement.innerHTML = `Time remaining: ${timers[messageId].timeRemaining} seconds`;
        } else {
            timerElement.innerHTML = "Time's Up!";
        }
    }
}

function disableSubmitButton(messageId) {
    const submitButton = document.querySelector(`#submit_${messageId}`);
    if (submitButton) {
        submitButton.disabled = true;
    }
}

function resetTimer(messageId) {
    timers[messageId].timeRemaining = 60;
    clearInterval(timers[messageId].interval);
    enableSubmitButton(messageId);
    updateTimerDisplay(messageId);
}

function enableSubmitButton(messageId) {
    const submitButton = document.querySelector(`#submit_${messageId}`);
    if (submitButton) {
        submitButton.disabled = false;
    }
}

function addGrade(messageJSON) {
    console.log(addGrade)
    const chatMessages = document.getElementById("grades-stud");
    chatMessages.innerHTML += "Question "+messageJSON["question"]+"; Answer "+ messageJSON["answer"] + " " +"Correct? "+messageJSON["correctornot"] +"</br>"
    chatMessages.scrollIntoView(false);
    chatMessages.scrollTop = chatMessages.scrollHeight - chatMessages.clientHeight;
}

function addGradeQuestions(messageJSON) {
    const chatMessages = document.getElementById("grades-all");
    chatMessages.innerHTML += "Question "+messageJSON["title"]+"; Answer "+ messageJSON["correctanswer"] + "</br></br>" 
    chatMessages.scrollIntoView(false);
    chatMessages.scrollTop = chatMessages.scrollHeight - chatMessages.clientHeight;
}

function submitAnswer(event, param,question_,username_) {
    event.preventDefault();
    console.log("submitanswercheck")
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }
    var options = Array.from(document.getElementsByName(param));
    console.log(options);
    var selected;
    for(var i = 0; i < options.length; i++){
        if(options[i].checked){
            selected = options[i].id;
        }
    }
    
    const correct_answer = document.getElementById("right-option");
    const correct_answer_value = correct_answer.options[correct_answer.selectedIndex].text;
    console.log("compfngwku4g check")
    console.log(selected)
    const messageJSON = {"selected": selected, "correctornot": selected == correct_answer_value};
    if(ws){
        console.log("websocketreceptioncheck")
        console.log("message_"+param+"_q")
        question_ = question_.toString()
        socket.send(JSON.stringify({'messageType': 'questionAnswer',"selected": selected, "correctornot": selected == correct_answer_value, "question":question_,"username":username_}));
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
    // console.log()
    if(ws){
        socket.send(JSON.stringify({'messageType': 'chatMessage',"title": title, "description": description,"choice1": choice1, "choice2": choice2, "choice3": choice3, "choice4": choice4, "correctanswer": correct_answer_value}));
        // time()
    }
    else{
        request.send(JSON.stringify(messageJSON));
        title_text_box.focus();
    }

}

function updateChat() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            // clearChat();
            const messages = JSON.parse(this.response);
            console.log(messages);
            for (const message of messages) {
                addMessageToChat(message);
            }
        }
    }
    request.open("GET", "/chat-history");
    request.send();
}

function seeGrade(){
    console.log("hello")
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            // clearChat();
            const messages = JSON.parse(this.response);
            console.log(messages);
            for (const message of messages) {
                addGrade(message);
            }
        }
    }
    request.open("GET", "/see-grade");
    request.send();
}

function seeGradeStudent(){
    console.log("hello")
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            // clearChat();
            const messages = JSON.parse(this.response);
            console.log(messages);
            for (const message of messages) {
                addGradeQuestions(message);
            }
        }
    }
    request.open("GET", "/see-grade-questions");
    request.send();
    // chatMessages.innerHTML += chatMessageHTML(messageJSON);
    // chatMessages.scrollIntoView(false);
    // chatMessages.scrollTop = chatMessages.scrollHeight - chatMessages.clientHeight;
}

function welcome2() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        console.log(this.response)
        if (this.readyState === 4 && this.status === 200) {
            // clearChat();
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addMessageToChat(message);
            }
        }
    }
    request.open("GET", "/grade");
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
    seeGrade();
    seeGradeStudent();

    if (ws) {
        initWS();
    } else {
        setInterval(updateChat, 2000);
        const videoElem = document.getElementsByClassName('video-chat')[0];
        videoElem.parentElement.removeChild(videoElem);
        setInterval(updateChat, 2000);
    }
}