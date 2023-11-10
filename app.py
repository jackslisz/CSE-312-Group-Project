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
from flask_sock import Sock

#Creating Flask app instance and storing it in app
#__name__ holds the name of current Python module
app = Flask(__name__, static_url_path="/static")
#Initializing the Database (DB)
db = db_init()

#Decorators to turn Python function home_page into Flask view function

sock = Sock(app)

# @app.route("/websocket")
# def application(env, start_response):
#     # complete the handshake
#     uwsgi.websocket_handshake(env['HTTP_SEC_WEBSOCKET_KEY'], env.get('HTTP_ORIGIN', ''))
#     while True:
#         msg = uwsgi.websocket_recv()
#         uwsgi.websocket_send(msg)

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
        response = make_response(render_template('index_template.html', username=db_result.get("username", 'Guest')))
    #Otherwise, replacing the template with the username "Guest"
    else:
        response = make_response(render_template('index_template.html', username='Guest'))
    #Setting the nosniff header
    response.headers['X-Content-Type-Options'] = 'nosniff'
    #Setting the correct MIME type for HTML
    response.headers['Content-Type'] = 'text/html; charset=utf-8'    
    #Returning the finished response
    return response

@sock.route('/websocket')
def echo(ws):
    while True:
        data = ws.receive()
        # print(data)
        # print(data)
        data = loads(data)
        auth_token_from_browser = request.cookies.get('auth_token', None)
    #Checking if the user has an auth token present
        if auth_token_from_browser is not None:
            #Hashing the token by calling the SHA256 function
            encrypt_auth_token = sha256(auth_token_from_browser.encode()).digest()
            #Checking whether the DB contains that auth token 
            if(get_auth_tokens(db, encrypt_auth_token)):
                #If so, updating the unique ID of the new message
                update_id(db)
                #Inserting the message into the DB using splicing
                print(get_auth_tokens(db, encrypt_auth_token)["username"])
                data["title"] = escape(data["title"])
                data["description"] = escape(data["description"])
                data["choice1"] = escape(data["choice1"])
                data["choice2"] = escape(data["choice2"])
                data["choice3"] = escape(data["choice3"])
                data["choice4"] = escape(data["choice4"])
                data["correctanswer"] = escape(data["correctanswer"])
                insert_message_websocket(db, data, get_auth_tokens(db, encrypt_auth_token)["username"])
                data.update({"username" : get_auth_tokens(db, encrypt_auth_token)["username"]})
                print(data)
        data = dumps(data)
        ws.send(data)

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
    #Calling send_from_directory to edit nosniff header of non-HTML files
    response = send_from_directory('static/img/', file_path)
    #Setting the nosniff header
    response.headers['X-Content-Type-Options'] = 'nosniff' 
    #Setting the correct MIME type for PNG images
    response.headers['Content-Type'] = 'image/png'    
    #Returning the finished response
    return response

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

#Decorator to turn Python function chat_message into Flask view function
@app.route('/chat-message', methods=["POST"])
def chat_message():
    #Retrieving the entire body of the request by calling get_data()
    body = request.get_data().decode()
    print(f"body: {body}")
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
    
#Decorator to turn Python function register_user into Flask view function
@app.route('/register', methods=["POST"])
def register_user():
    #Retrieving the entire body of the request by calling get_data()
    creds = request.get_data().decode()
    #Splitting the body to store the username (0) and password (1) inside creds
    creds = creds.split('&', 1)
    #Removing key from username/password to leave just the username/password
    creds[0] = creds[0].replace("username_reg=", "")
    creds[1] = creds[1].replace("password_reg=", "")
    #Escaping any HTML tags that user put in their username
    creds[0] = escape(creds[0])
    #Inserting creds into DB by calling function from dbhandler.py
    store_creds(db, creds)
    #Removing the password from the credentials array
    creds[1] = ""
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

@app.route("/submit-answer",methods=["POST"])
def submit_answer():
    return redirect(url_for('home_page'))


#Decorator to turn Python function like_message into Flask view function
@app.route("/chat-like", methods=["POST"])
def like_message():
    #Retrieving the entire body of the request by calling get_data()
    body = request.get_data().decode()
    #Splitting the body at the colon to separate the message
    #Retrieving the auth token from the user's browser
    auth_token_from_browser  =request.cookies.get('auth_token', None)
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
    app.run(host='0.0.0.0', port='8080')