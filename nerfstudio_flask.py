import flask
import subprocess
import os
import threading
import sys
import time

app = flask.Flask(__name__)

output_path = ""
@app.route('/')
def home_page():
    return flask.render_template("frontend.html")


@app.route('/', methods=['POST'])
def send_video():
    uploaded_video = flask.request.files['file']
    
    global output_path
    global processing_completed
    if uploaded_video.filename != "":
        data_path = uploaded_video.filename + "_data"
        
        os.mkdir(data_path)
        
        uploaded_video.save(os.path.join(data_path, uploaded_video.filename))
        
        video_path = os.path.join(data_path, uploaded_video.filename)
        
        output_path = uploaded_video.filename + "_output"
    
    print("Using COLMAP to process video...")
    ns_process_command = ["ns-process-data", "video", "--data", video_path, "--output-dir", output_path]
    subprocess.run(ns_process_command)
    processing_completed = False

    thread = threading.Thread(target=train_model)
    thread.start()
    
    sys.exit()


def train_model():
    global processing_completed
    processing_completed = True
    print("Training...")
    subprocess.run(["ns-train", "splatfacto", "--data", output_path])
    
if __name__ == "__main__": 
    app.run(debug=True, host='0.0.0.0', port=8008)