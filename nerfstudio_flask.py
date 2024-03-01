import flask
import subprocess
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
        
        output_path = "./" + uploaded_video.filename + "_output"
    
    print("Using COLMAP to process video...")
    ns_process_command = ["ns-process-data", "video", "--data", data_path, "--output-dir", output_path]
    subprocess.run(ns_process_command)
    
    print("Training data...")
    ns_train_command = ["ns-train", "splatfacto", "--data", data_path]
    subprocess.run(ns_train_command)
    
    return flask.redirect(flask.url_for("home_page"))

if __name__ == "__main__": 
    app.run(debug=True, host='0.0.0.0', port=7007)