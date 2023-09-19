#Importing Flask framework and render_template, make_response, and request modules
from flask import Flask, render_template, make_response, request

#Creating Flask app instance and storing it in app
#__name__ holds the name of current Python module
app = Flask(__name__)

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

#Checking if __name__ is the name of top-level environment of program
if __name__ == "__main__":
    #If so, calling run (on app) on the local host and port 8080
    app.run(debug=True, host='0.0.0.0', port='8080')