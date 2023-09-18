#Importing Flask framework and render_template module
from flask import Flask, render_template

#Creating Flask app instance and storing it in app
#__name__ holds the name of current Python module
app = Flask(__name__)

#Decorator to turn Python function home_page into Flask view function
@app.route("/")
def home_page():
    #Calling render_template to look and open the file index.html
    return render_template('index.html')

#Checking if __name__ is the name of top-level environment of program
if __name__ == "__main__":
    #If so, calling run (on app) on the local host and port 8080
    app.run(host='0.0.0.0', port='8080')