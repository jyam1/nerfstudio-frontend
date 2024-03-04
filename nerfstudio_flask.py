import flask
from flask import jsonify
import subprocess
import os

app = flask.Flask(__name__)

output_path = ""
processing_completed = False

def upload_video(uploaded_video, output_path, video_path):
    if uploaded_video.filename != "":
        data_path = uploaded_video.filename + "_data"
        
        os.mkdir(data_path)
        
        uploaded_video.save(os.path.join(data_path, uploaded_video.filename))
        
        video_path = os.path.join(data_path, uploaded_video.filename)
        
        output_path = uploaded_video.filename + "_output"

def process_colmap(video_path, output_path):
    print("Using COLMAP to process video...")
    ns_process_command = ["ns-process-data", "video", "--data", video_path, "--output-dir", output_path]
    subprocess.run(ns_process_command)

def train_data(output_path):
    print("Training...")
    train_command = ["ns-train", "splatfacto", "--data", output_path]
    subprocess.run(train_command)

@app.route('/')
def home_page():
    return flask.render_template("frontend.html")

@app.route('/status')
def process_status():
    if processing_completed:
        return "Video processing complete. Training data in progress..."
    else:
        return "Processing video using Colmap..."

@app.route('/', methods=['POST'])
def send_video():
    uploaded_video = flask.request.files['file']
    
    global output_path
    global processing_completed 
    video_path = None
    
    upload_video(uploaded_video, output_path, video_path)
    
    process_colmap(video_path, output_path)
    
    train_data(output_path)
    
    processing_completed = False
    os._exit(0)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=7007)