import flask
import subprocess
import os

app = flask.Flask(__name__)

output_path = ""
processing_completed = False

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# F U N C T I O N S
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

'''
 Function:      upload_video
 Purpose:       Frontend allows user to upload video and writes into kubernetes pod
 Parameters:    
    (file)uploaded_video:   User's uploaded video
    (str)output_path:       Path to output of processed video
    (str)video_path:        Path to uploaded video
 Returns:
    N/A
'''
def upload_video(uploaded_video, output_path, video_path):
    if uploaded_video.filename != "":
        
        #make data directory
        data_path = uploaded_video.filename + "_data"
        os.mkdir(data_path)
        
        #save video in pod
        uploaded_video.save(os.path.join(data_path, uploaded_video.filename))
        
        #make path for video and output
        video_path = os.path.join(data_path, uploaded_video.filename)
        output_path = uploaded_video.filename + "_output"

'''
 Function:      process_colmap
 Purpose:       Process video through COLMAP
 Parameters:    
    (str)video_path:    Path to uploaded video
    (str)output_path:   Path to output of processed video
 Returns:
    N/A
'''
def process_colmap(video_path, output_path):
    print("Using COLMAP to process video...")
    
    #run command for COLMAP processing
    ns_process_command = ["ns-process-data", "video", "--data", video_path, "--output-dir", output_path]
    subprocess.run(ns_process_command)

'''
 Function:      train_data
 Purpose:       Train processed data through splatfacto model
 Parameters:    
    (str)output_path:               Path to output of processed video
    (bool)processing_completed:     Tells whether processing for COLMAP is finished
 Returns:
    N/A
'''
def train_data(output_path, processing_completed):
    #processing finished
    processing_completed = True
    
    print("Training...")
    
    #run command to train data in splatfacto model
    train_command = ["ns-train", "splatfacto", "--data", output_path]
    subprocess.run(train_command)

'''
 Function:      home_page
 Purpose:       Home page of frontend
 Parameters:    
    N/A
 Returns:
    N/A
'''
@app.route('/')
def home_page():
    return flask.render_template("frontend.html")

'''
 Function:      process_status
 Purpose:       Process status for COLMAP, sends signal to frontend to notify users
 Parameters:    
    N/A
 Returns:
    N/A
'''
@app.route('/status')
def process_status():
    if processing_completed:
        return "Video processing complete. Training data in progress..."
    else:
        return "Processing video using Colmap..."

'''
 Function:      send_video
 Purpose:       Allows user to send video, process data, and train data
 Parameters:    
    N/A
 Returns:
    N/A
'''
@app.route('/', methods=['POST'])
def send_video():
    uploaded_video = flask.request.files['file']
    
    global output_path
    global processing_completed 
    video_path = None
    
    upload_video(uploaded_video, output_path, video_path)
    process_colmap(video_path, output_path)
    processing_completed = False
    train_data(output_path, processing_completed)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=7007)