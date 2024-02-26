import flask
import os

app = flask.Flask(__name__)

@app.route('/', methods=['GET'])
def home_page():
    return flask.render_template("frontend.html")

@app.route('/', methods=['POST'])
def send_video():
    uploaded_video = flask.request.files['file']
    
    if uploaded_video.filename != "":
        data_path = "./" + uploaded_video.filename + "_data"
        
        os.mkdir(data_path)
        
        uploaded_video.save(os.path.join(data_path, uploaded_video.filename))
    
    return flask.redirect(flask.url_for("home_page"))
    
if __name__ == "__main__":
    app.run(debug=True)