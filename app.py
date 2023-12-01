#Importing Flask, json, secrets, hashlib, and bcrypt modules
from flask import *
from json import *
from secrets import *
from hashlib import *
from bcrypt import *
#Importing HTML escape function
from html import escape
#Importing functions from dbhandler.py
from util.dbhandler import *
# from uswgi import *
from bson import json_util
from flask_sock import Sock
from flask_socketio import SocketIO, emit

# TODO : 
# FIX WEBSOCKETS NOT SENDING TO ALL CONNECTIONS
# FIX TIMER

#Creating Flask app instance and storing it in app
#__name__ holds the name of current Python module
app = Flask(__name__, static_url_path="/static")
#Initializing the Database (DB)
db = db_init()
#Decorators to turn Python function home_page into Flask view function
# sock = SocketIO(app)
app.config['SECRET_KEY'] = 'secret!'
sock = SocketIO(app)

all_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": "thecodedeamons@gmail.com",
    "MAIL_PASSWORD": "none"
}
app.config.update(all_settings)
mail = Mail(app)

#Creating a global variable to hold the set of all WS connections
global ws_set
ws_set = set()

@app.route("/")
@app.route("/home", methods=["GET", "POST"])
def home_page():
    #Retrieving the authentication token from browser
    auth_token_from_browser = request.cookies.get('auth_token', None)
    #Checking if the user has an auth token present
    if auth_token_from_browser is not None:
        #If so, hashing the token by calling the SHA256 function
        encrypt_auth_token = sha256(auth_token_from_browser.encode()).digest()
        #Checking whether the DB contains that auth token, if not setting db_result to hold an empty dictionary
        db_result = get_auth_tokens(db, encrypt_auth_token) if get_auth_tokens(db, encrypt_auth_token) != None else {}
        #If so, calling render_template to look for and open the file index.html
        #Calling make_response to make a flask response to edit headers and MIME types
        try:
            if(not db_result["email_verified"]):
                response = make_response(render_template('index_template.html', verification="You need to verify your email!",username=db_result.get("username", 'Guest')))
            else:
                response = make_response(render_template('index_template.html', verification="You have been verified!",username=db_result.get("username", 'Guest')))
        except Exception as e:
                response = make_response(render_template('index_template.html', verification="You need to verify your email!",username=db_result.get("username", 'Guest')))

    #Otherwise, replacing the template with the username "Guest"
    else:
        response = make_response(render_template('index_template.html', username='Guest'))
    #Setting the nosniff header
    response.headers['X-Content-Type-Options'] = 'nosniff'
    #Setting the correct MIME type for HTML
    response.headers['Content-Type'] = 'text/html; charset=utf-8'    
    #Returning the finished response
    return response

@sock.on('ws', namespace='/websocket')
def echo(ws):
    global ws_set
    #Adding the current WS connection to the set of connections
    print(ws)
    ws_set.add(ws)
    print(ws_set)
    data = b''
    while True:
    #     leave_loop = False
    #     try:
    #         data = ws.receive()
    #     except:
    #         #if the connection was terminated, remove them from teh set and break
    #         leave_loop = True
    #     if data == b'': 
    #         leave_loop = True
    #     if leave_loop:
    #         ws_set.remove(ws)
    #         break
    #     print("\n\n\n\n\nHERE:")
    #     print(data)
        # print(data)
        # data = loads(data)
        data = loads(json)
        # print(data)
        auth_token_from_browser = request.cookies.get('auth_token', None)
        #Checking if the user has an auth token present
        if auth_token_from_browser is not None:
            #Hashing the token by calling the SHA256 function
            encrypt_auth_token = sha256(auth_token_from_browser.encode()).digest()
            #Checking whether the DB contains that auth token 
            if(get_auth_tokens(db, encrypt_auth_token)):
                #Checking if the incoming request is a new message
                if data["messageType"] == "chatMessage":
                    #If so, updating the unique ID of the new message
                    update_id(db)
                    #Inserting the message into the DB using splicing
                    # print(get_auth_tokens(db, encrypt_auth_token)["username"])
                    data["title"] = escape(data["title"])
                    data["description"] = escape(data["description"])
                    data["choice1"] = escape(data["choice1"])
                    data["choice2"] = escape(data["choice2"])
                    data["choice3"] = escape(data["choice3"])
                    data["choice4"] = escape(data["choice4"])
                    data["correctanswer"] = escape(data["correctanswer"])
                    # if(data["username"])
                    id_ = insert_message_websocket(db, data, get_auth_tokens(db, encrypt_auth_token)["username"])
                    # print(id_)
                    data.update({"username" : get_auth_tokens(db, encrypt_auth_token)["username"]})
                    data.update({"id":id_})
                    # if()
                    # get_data = get_file(db)
                    # if(get_data["image"]!=None):
                    #     data.update({"image":get_data["image"]})
                    # else:
                    #     data.update({"image":"quizicon.ico"})
                    # data.update({"id" : get_auth_tokens(db, encrypt_auth_token)["username"]})
                    # print(data)
                #Checking if the incoming request is an answer to a question
                elif data["messageType"] == "questionAnswer":
                    # if(data["correctornot"] == True):
                    if(get_auth_tokens(db, encrypt_auth_token)["username"]==data["username"]):
                        pass
                    else:
                        print(get_auth_tokens(db, encrypt_auth_token)["username"])
                        print(data["username"])
                        answer(db,data,data["correctornot"],get_auth_tokens(db, encrypt_auth_token)["username"])
                    # else:

                    #"selected": selected, "correctornot": selected == correct_answer_value}));
                # mute
                    # data["selected":selected]
                data = dumps(data)
                # print("sending",data)
                #Sending the WS response using send for each socket connection
                # send_to_all(data)
                emit("ws response", data, broadcast=True)

# def send_to_all(data):
#     global ws_set
#     print(f'There are {len(ws_set)} connections: they are: {ws_set}')
#     for socket in ws_set:
#         if not socket.close:
#             socket.send(data)
#             print(f"Data sent to: {socket}")

#Decorator to turn Python function style_page into Flask view function
@app.route('/static/css/<path:file_path>')
def style_page(file_path):
    #Calling send_from_directory to edit nosniff header of non-HTML files
    response = send_from_directory('static/css/', file_path)
    #Setting the nosniff header
    response.headers['X-Content-Type-Options'] = 'nosniff' 
    #Setting the correct MIME type for CSS
    response.headers['Content-Type'] = 'text/css; charset=utf-8'    
    #Returning the finished response
    return response

#Decorator to turn Python function script_page into Flask view function
@app.route('/static/js/<path:file_path>')
def script_page(file_path):
    #Calling send_from_directory to edit nosniff header of non-HTML files
    response = send_from_directory('static/js/', file_path)
    #Setting the nosniff header
    response.headers['X-Content-Type-Options'] = 'nosniff' 
    #Setting the correct MIME type for JavaScript
    response.headers['Content-Type'] = 'text/javascript; charset=utf-8'    
    #Returning the finished response
    return response

#Decorator to turn Python function image_page into Flask view function
@app.route('/static/img/<path:file_path>')
def image_page(file_path):
    #Removing any slashes to avoid users requesting server files
    new_file_path = file_path.replace("/", "")
    #Calling send_from_directory to edit nosniff header of non-HTML files
    response = send_from_directory('static/img/', new_file_path)
    #Setting the nosniff header
    response.headers['X-Content-Type-Options'] = 'nosniff' 
    #Setting the correct MIME type for PNG images
    response.headers['Content-Type'] = 'image/png'    
    #Returning the finished response
    return response

# app.config.update(all_settings)
@app.route('/nu')
def email():
    # with app.config():
    # msg = Message(subject="Email",
    #                     sender="codedemons@gmail.com",
    #                     recipients=["longhornlewis966@gmail.com"], # replace with your email for testing
    #                     body="This is a test email I sent with Gmail and Python!")
    # mail.send(msg)
    token = request.args.get("token")
    username = request.args.get("username")


#Decorator to turn Python function visit_counter_cookie into Flask view function
@app.route("/visit-counter")
def visit_counter_cookie():
    #Assigning the value held in the visit_counter cookie to visit_count (0 by default)
    visit_count = request.cookies.get('visit_counter', 0)
    #Calling make_response to make a flask response to use set_cookie
    response = make_response(f"Visit count: {int(visit_count) + 1}")
    #Calling set_cookie to set a new visit_counter cookie with an updated value
    response.set_cookie('visit_counter', str(int(visit_count) + 1), max_age=3600) 
    #Returning the finished response
    return response

@app.route('/see-grade', methods=["GET", "POST"])
def grade():
    auth_token_from_browser = request.cookies.get('auth_token', None)
    #Checking if the user has an auth token present
    if auth_token_from_browser is not None:
        #If so, hashing the token by calling the SHA256 function
        encrypt_auth_token = sha256(auth_token_from_browser.encode()).digest()
        #Checking whether the DB contains that auth token, if not setting db_result to hold an empty dictionary
        # db_result = get_auth_tokens(db, encrypt_auth_token) if get_auth_tokens(db, encrypt_auth_token) != None else {}
        db_result = get_auth_tokens(db, encrypt_auth_token) 
        if get_auth_tokens(db, encrypt_auth_token) != None:
            #If so, calling render_template to look for and open the file index.html
            #Calling make_response to make a flask response to edit headers and MIME types
            usernm = get_grades(db, get_auth_tokens(db, encrypt_auth_token)["username"])
            users = []
            for m in usernm:
                users.append(m)
            return json_util.dumps(users).encode()
        # response = make_response(render_template('bo.html', username=users))
    # #Otherwise, replacing the template with the username "Guest"
    # else:
    #     response = make_response(render_template('index_template.html', username='Guest'))
    # #Setting the nosniff header
    # response.headers['X-Content-Type-Options'] = 'nosniff'
    # #Setting the correct MIME type for HTML
    # response.headers['Content-Type'] = 'text/html; charset=utf-8'    
    #Returning the finished response
    # if(users)
        try:
            # print(json_util.dumps(users))
            return abort(401)
        except Exception as e:
            make_response(f"")

    else:
        make_response(f"")

@app.route('/see-grade-questions', methods=["GET", "POST"])
def grade_get():
    auth_token_from_browser = request.cookies.get('auth_token', None)
    #Checking if the user has an auth token present
    if auth_token_from_browser is not None:
        #If so, hashing the token by calling the SHA256 function
        encrypt_auth_token = sha256(auth_token_from_browser.encode()).digest()
        #Checking whether the DB contains that auth token, if not setting db_result to hold an empty dictionary
        # db_result = get_auth_tokens(db, encrypt_auth_token) if get_auth_tokens(db, encrypt_auth_token) != None else {}
        db_result = get_auth_tokens(db, encrypt_auth_token) 
        if get_auth_tokens(db, encrypt_auth_token) != None:
            #If so, calling render_template to look for and open the file index.html
            #Calling make_response to make a flask response to edit headers and MIME types
            usernm = get_chat_history_particular_username(db, get_auth_tokens(db, encrypt_auth_token)["username"])
            users = []
            for m in usernm:
                users.append(m)
            return json_util.dumps(users).encode()
        # response = make_response(render_template('bo.html', username=users))
    # #Otherwise, replacing the template with the username "Guest"
    # else:
    #     response = make_response(render_template('index_template.html', username='Guest'))
    # #Setting the nosniff header
    # response.headers['X-Content-Type-Options'] = 'nosniff'
    # #Setting the correct MIME type for HTML
    # response.headers['Content-Type'] = 'text/html; charset=utf-8'    
        #Returning the finished response
        try:
            print(json_util.dumps(users))

            return json_util.dumps(users).encode()
        except Exception as e:
            make_response(f"")
    #Returning the finished response
    # print(json_util.dumps(users))
    return abort(401)

#Decorator to turn Python function chat_message into Flask view function
@app.route('/chat-message', methods=["POST"])
def chat_message():
    #Retrieving the entire body of the request by calling get_data()
    body = request.get_data().decode()
    # print(f"body: {body}")
    #Splitting the body at the comma to separate the title from the description
    body = body.split(",", -1)
    for element in range(len(body)):
        body[element] = body[element].split(":")[1].replace("\"","")
        body[element] = body[element].replace("{","")
        body[element] = body[element].replace("}","")
    # print(body)
    #Removing the key from the title value, leaving just the title the user entered
    # body[0] = body[0].replace("{\"title\":\"", "")
    # body[0] = body[0][0:-1]
    #Removing the key from the description value, leaving just the description the user entered
    # body[1] = body[1].replace("\"description\":\"", "")
    # body[1] = body[1][0:-2]
    #Retrieving the authentication token
    auth_token_from_browser = request.cookies.get('auth_token', None)
    #Checking if the user has an auth token present
    if auth_token_from_browser is not None:
        #Hashing the token by calling the SHA256 function
        encrypt_auth_token = sha256(auth_token_from_browser.encode()).digest()
        #Checking whether the DB contains that auth token 
        if(get_auth_tokens(db, encrypt_auth_token)):
            #If so, updating the unique ID of the new message
            update_id(db)
            # print("e", encrypt_auth_token)
            # print(get_auth_tokens(db, encrypt_auth_token))
            #Inserting the message into the DB using splicing
            insert_message(db, body, get_auth_tokens(db, encrypt_auth_token)["username"])
    #Calling make_response to make an empty flask response
    return make_response(f"")

#Decorator to turn Python function chat_history into Flask view function
#Commented to test functionality of websocket. If this is commented and new chat messages appear, websocket is the only functionality that enables this.
@app.route('/chat-history')
def chat_history():
    #Checking if the chat's history is not empty
    if get_chat_history(db):
        #Dumping the entire chat history into a JSON string
        chat_history = dumps(list(get_chat_history(db))).encode()
        #Calling make_response to make a response using the JSON object in chat_history
        return make_response(chat_history)
    

@app.route("/mail")
def m():
    token = request.args.get("token")
    user=request.args.get("username")
    verified = verify_email(db,token,user)
    return redirect(url_for('home_page'))

#Decorator to turn Python function register_user into Flask view function
@app.route('/register', methods=["POST"])
def register_user():
    # print(request.get_data())
    #Retrieving the entire body of the request by calling get_data()
    creds = request.get_data().decode()
    # print(creds)
    #Splitting the body to store the username (0) and password (1) inside creds
    creds = creds.split('&')
    #Removing key from username/password to leave just the username/password
    creds[0] = creds[0].replace("username_reg=", "")
    creds[2] = creds[2].replace("password_reg=", "")
    creds[1] = creds[1].replace("email_reg=", "")
    print(creds)
    #Escaping any HTML tags that user put in their username
    creds[0] = escape(creds[0])
    #Inserting creds into DB by calling function from dbhandler.py
    creds_stored = store_creds(db, creds)
    #Removing the password from the credentials array
    creds[2] = ""
        # if(authentication_attempt):
        #If successful, create, Hash and store a random auth token
    gen_auth_token = token_urlsafe(80)
    # creds[1] = escape(creds[1])
    #Calling gen_auth_token to generate a new auth token value for user
    encrypt_auth_token = gen_auth_token
    #Hashing the token by calling the SHA256 function
    # encrypt_auth_token = sha256(encrypt_auth_token.encode()).digest()
    #Calling add_auth to add the token to the DB
    token = add_email_token(db, creds,creds_stored, encrypt_auth_token)
    #Calling make_response to make and send a Flask response
    response = redirect(url_for('home_page'))
    print(creds[1])
    msg = Message(subject="Verify your email",
                        sender="codedemons@gmail.com",
                        recipients=[creds[1].split("%40")[0]+"@"+creds[1].split("%40")[1]], # replace with your email for testing
                        body="Thank you for signing up for the code demons app!\n\nIn order to continue, you must verify your email. Click the link below to do so! \nhttp://localhost:8080/mail?token="+ token+"&username="+creds[0])
    mail.send(msg)

    #Make cookie of auth_token
    # response.set_cookie('auth_token', gen_auth_token, max_age=3600, httponly=True) 
    #Sending a redirect to the home page by calling redirect() and url_for()
    return redirect(url_for('home_page'))


#Decorator to turn Python function login_page into Flask view function
@app.route("/login", methods=["POST"])
def login_page():
    #Retrieve the data 
    json_log_data = request.get_data().decode().split("&")
    #Obtain the unencrypted password
    unencrypted_password = json_log_data[1].split("=")[1]
    #Obtain username
    username = json_log_data[0].split("=")[1]
    #Run a function to check whether the username and password match in the DB
    authentication_attempt = check_creds(db, [username, unencrypted_password])
    if(authentication_attempt):
        #If successful, create, Hash and store a random auth token
        gen_auth_token = token_urlsafe(16)
        #Calling gen_auth_token to generate a new auth token value for user
        encrypt_auth_token = gen_auth_token
        #Hashing the token by calling the SHA256 function
        encrypt_auth_token = sha256(encrypt_auth_token.encode()).digest()
        #Calling add_auth to add the token to the DB
        add_auth(db, authentication_attempt, encrypt_auth_token)
        #Calling make_response to make and send a Flask response
        response = redirect(url_for('home_page'))
        #Make cookie of auth_token
        response.set_cookie('auth_token', gen_auth_token, max_age=3600, httponly=True) 
    #Otherwise, returning error message 401
    else:
        response = abort(401)
    #Returning the Flask response
    return response

#Decorator to turn Python function login_page into Flask view function
@app.route("/image", methods=["POST"])
def image():
    #Retrieving the authentication token from browser
    auth_token_from_browser = request.cookies.get('auth_token', None)
    #Checking if the user has an auth token present
    if auth_token_from_browser is not None:
        #Hashing the token by calling the SHA256 function
        encrypt_auth_token = sha256(auth_token_from_browser.encode()).digest()
        #Checking whether the DB contains that auth token 
        if(get_auth_tokens(db, encrypt_auth_token)):
            #Retrieve the data 
            if request.files:
                file = request.files["upload"]
                if file.filename == "":
                    return redirect(url_for('home_page'))
                image_name = insert_image(db)
                file.save(image_name)
    
    # Obtain the unencrypted password
    # Obtain username
    # username = json_log_data[0].split("=")[1]
    # Run a function to check whether the username and password match in the DB
    # authentication_attempt = check_creds(db, [username, unencrypted_password])
    # if(authentication_attempt):
    #     #If successful, create, Hash and store a random auth token
    #     gen_auth_token = token_urlsafe(16)
    #     #Calling gen_auth_token to generate a new auth token value for user
    #     encrypt_auth_token = gen_auth_token
    #     #Hashing the token by calling the SHA256 function
    #     encrypt_auth_token = sha256(encrypt_auth_token.encode()).digest()
    #     #Calling add_auth to add the token to the DB
    #     add_auth(db, authentication_attempt, encrypt_auth_token)
    #     #Calling make_response to make and send a Flask response
    #     #Make cookie of auth_token
    #     response.set_cookie('auth_token', gen_auth_token, max_age=3600, httponly=True) 
    # #Otherwise, returning error message 401
    # else:
    #     response = abort(401)
    #Returning the Flask response
    return redirect(url_for('home_page'))
        
@app.route("/submit-answer", methods=["POST"])
def submit_answer():
    #Retrieving the authentication token
    auth_token_from_browser = request.cookies.get('auth_token', None)
    #Checking if the user has an auth token present
    if auth_token_from_browser is not None:
        #Hashing the token by calling the SHA256 function
        encrypt_auth_token = sha256(auth_token_from_browser.encode()).digest()
        #Checking whether the DB contains that auth token 
        if(get_auth_tokens(db, encrypt_auth_token)):
            pass

    return redirect(url_for('home_page'))

#Decorator to turn Python function like_message into Flask view function
@app.route("/chat-like", methods=["POST"])
def like_message():
    #Retrieving the entire body of the request by calling get_data()
    body = request.get_data().decode()
    #Splitting the body at the colon to separate the message
    #Retrieving the auth token from the user's browser
    auth_token_from_browser = request.cookies.get('auth_token', None)
    # SH256 encrypting auth token to check with DB. This is to ensure only logged-in users are able to like
    #Checking if there is any auth token in the browser
    if(auth_token_from_browser):
        #If so, hashing the token by calling the SHA256 function
        encrypt_auth_token = sha256(auth_token_from_browser.encode()).digest()
        #Call function to like/unlike a message
        get_msg_and_like(db, encrypt_auth_token, json.loads(body)["messageId"])
    #Calling make_response to make and send a Flask response
    return redirect(url_for('home_page'))

#Checking if __name__ is the name of top-level environment of program
if __name__ == "__main__":
    #If so, calling run (on app) on the local host and port 8080
    sock.run(app, host='0.0.0.0', port='8080', allow_unsafe_werkzeug=True)