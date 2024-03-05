import flask
import subprocess
import os

app = flask.Flask(__name__)

processing_completed = False
training_completed = False

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
def upload_video(uploaded_video):
    if uploaded_video.filename != "":
        
        #make data directory
        data_path = uploaded_video.filename + "_data"
        os.mkdir(data_path)
        
        #save video in pod
        uploaded_video.save(os.path.join(data_path, uploaded_video.filename))
        
        #make path for video and output
        video_path = os.path.join(data_path, uploaded_video.filename)
        output_path = uploaded_video.filename + "_output"
        
        return video_path, output_path

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
    global training_completed
    global processing_completed
    
    # Check if both processing and training are completed
    if processing_completed and training_completed:
        return "Video processing complete. Training complete."
    elif processing_completed:
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
    
    global processing_completed 
    processing_completed = False
    
    video_path, output_path = upload_video(uploaded_video)
    
    return flask.redirect(flask.url_for('process_colmap', output_path = output_path, video_path = video_path))

'''
 Function:      process_colmap
 Purpose:       Process video through COLMAP
 Parameters:    
    (str)video_path:    Path to uploaded video
    (str)output_path:   Path to output of processed video
 Returns:
    N/A
'''
@app.route('/process_colmap/<video_path>/<output_path>')
def process_colmap(output_path, video_path):
    print("Using COLMAP to process video...")
    
    #run command for COLMAP processing
    ns_process_command = ["ns-process-data", "video", "--data", video_path, "--output-dir", output_path]
    subprocess.run(ns_process_command)
    
    return flask.redirect(flask.url_for('train_data', output_path = output_path))

'''
 Function:      train_data
 Purpose:       Train processed data through splatfacto model
 Parameters:    
    (str)output_path:               Path to output of processed video
    (bool)processing_completed:     Tells whether processing for COLMAP is finished
 Returns:
    N/A
''' 
@app.route("/train_data/<output_path>")
def train_data(output_path):
    output_path = flask.request.args.get('output_path')
    
    global processing_completed
    global training_completed
    processing_completed = True 
    
    print("Training...")
    
    #run command to train data in splatfacto model
    train_command = ["ns-train", "splatfacto", "--data", output_path]
    subprocess.run(train_command)
    training_completed = True
    
    return "Training finished"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8008)