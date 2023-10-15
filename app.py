#Importing Flask framework and render_template, make_response, request, and send_from_directory modules
from flask import Flask, render_template, make_response, request, send_from_directory
#Importing JSON module
from json import *
#Importing functions from dbhandler.py
from util.dbhandler import *

#Creating Flask app instance and storing it in app
#__name__ holds the name of current Python module
app = Flask(__name__)
#Initializing the Database (DB)
db = db_init()

#Decorators to turn Python function home_page into Flask view function
@app.route("/")
@app.route("/home")
def home_page():
    #Calling render_template to look for and open the file index.html
    #Calling make_response to make a flask response to edit headers and MIME types
    response = make_response(render_template('index.html'))
    #Setting the nosniff header
    response.headers['X-Content-Type-Options'] = 'nosniff'
    #Setting the correct MIME type for HTML
    response.headers['Content-Type'] = 'text/html; charset=utf-8'    
    #Returning the finished response
    return response

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
    #Updating the unique ID of the new message
    update_id(db)
    #Retrieving the entire body of the request by calling get_data()
    body = request.get_data().decode()
    #Splitting the body at the colon to separate the message
    body = body.split(":", 1)
    #Inserting the message into the DB using splicing
    insert_message(db, body[1][1:-2])
    #Calling make_response to make an empty flask response
    return make_response(f"")

#Decorator to turn Python function chat_history into Flask view function
@app.route('/chat-history')
def chat_history():
    #Checking if the chat's history is not empty
    if get_chat_history(db):
        #Dumping the entire chat history into a JSON string
        chat_history = dumps(list(get_chat_history(db))).encode()
        #Calling make_response to make a response using the JSON object in chat_history
        return make_response(chat_history)
    #Otherwise, calling make_response to make an empty flask response
    else:
        return make_response(f"")

#Checking if __name__ is the name of top-level environment of program
if __name__ == "__main__":
    #If so, calling run (on app) on the local host and port 8080
    app.run(host='0.0.0.0', port='8080')