from flask import Flask

app = Flask(__name__)

@app.route("/")
def home_page():
    return "<h1>Hello!<h1> This is the home page."

if __name__ == "__main__":
    app.run()