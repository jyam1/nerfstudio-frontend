import flask
import os

app = flask.Flask(__name__)

@app.route('/')
def home_page():
    return flask.render_template("frontend.html")

if __name__ == "__main__":
    app.run(debug=True)