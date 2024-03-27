import flask
import subprocess
import os

app = flask.Flask(__name__)

# Note for some reason using a string status doesn't work
processing_completed = False
training_completed = False
video_uploaded = False

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

        # Make data directory
        data_path = uploaded_video.filename + "_data"
        os.mkdir(data_path)
        
        # Save video in pod
        uploaded_video.save(os.path.join(data_path, uploaded_video.filename))

        # Make path for video and output
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

@app.route('/showcase')
def showcase_page():
    return flask.render_template("showcase.html")


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
    global video_uploaded

    if video_uploaded:
        if processing_completed and not training_completed:
            return "Initializing GPUs for training..."
        elif not (processing_completed or training_completed):
            return "Processing video..."
    else:
        return ""

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
    global processing_completed
    global video_uploaded  
    global training_completed

    uploaded_video = flask.request.files['file']
    
    video_path, output_path = upload_video(uploaded_video)
    video_uploaded = True

    process_colmap(video_path, output_path)
    processing_completed = True

    train_data(output_path)
    training_completed = True

    return ""
    

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
    
    # Run command for COLMAP processing
    print("Process")
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
def train_data(output_path):

    # Run command to train data in splatfacto model
    print("Training...")
    train_command = ["ns-train", "splatfacto", "--data", output_path]
    subprocess.run(train_command)
      
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8008)