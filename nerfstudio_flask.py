import flask
import subprocess
import os
import signal

app = flask.Flask(__name__)

output_path = ""

@app.route('/')
def home_page():
    return flask.render_template("frontend.html")

@app.route('/', methods=['POST'])
def send_video():
    uploaded_video = flask.request.files['file']
    print(uploaded_video)
    
    if uploaded_video.filename != "":
        data_path = uploaded_video.filename + "_data"
        
        os.mkdir(data_path)
        
        uploaded_video.save(os.path.join(data_path, uploaded_video.filename))
        
        video_path = os.path.join(data_path, uploaded_video.filename)
        
        output_path = uploaded_video.filename + "_output"
    
    print("Using COLMAP to process video...")
    ns_process_command = ["ns-process-data", "video", "--data", video_path, "--output-dir", output_path]
    subprocess.run(ns_process_command)
    
    shutdown_server()
    os.kill(os.getpid(), signal.SIGINT)

def shutdown_server():
    func = flask.request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    
if __name__ == "__main__": 
    app.run(debug=True, host='0.0.0.0', port=7007)
    
    print("Training...")
    subprocess.run(["ns-train", "splatfacto", "--data", output_path])