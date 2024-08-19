import cv2
from ultralytics import YOLO
import numpy as np
import time
import configparser
import os
import subprocess


TIME_PER_FRAME_FACE = 0.0031355378818845 #minutes
TIME_PER_FRAME_HEAD = 0.02867874396 #minutes


class VideoCutter:
    def __init__(self, input_path, ffmpeg_path='ffmpeg'):
        self.input_path = input_path
        self.ffmpeg_path = ffmpeg_path

    def cut_video(self, start_time, duration):
        import subprocess
        import os

        # Ensure ffmpeg path is correct
        if not os.path.isfile(self.ffmpeg_path):
            raise FileNotFoundError(f"ffmpeg executable not found at {self.ffmpeg_path}")

        # Generate output path based on input path
        output_dir, input_filename = os.path.split(self.input_path)
        output_filename = 'cut_' + input_filename
        self.output_path = os.path.join(output_dir, output_filename)
        
        # Check if the output file already exists and overwrite it
        if os.path.exists(self.output_path):
            os.remove(self.output_path)  # Remove the existing file

        # ffmpeg command to cut the video
        command = [
            self.ffmpeg_path,        # Full path to ffmpeg executable
            '-i', self.input_path,   # Input file
            '-ss', str(start_time),  # Start time
            '-t', str(duration),     # Duration
            '-c:v', 'copy',          # Copy video codec (no re-encoding)
            '-c:a', 'copy',          # Copy audio codec (no re-encoding)
            self.output_path         # Output file
        ]
        subprocess.run(command, check=True)

        # Check if the output file was created
        if not os.path.exists(self.output_path):
            raise FileNotFoundError(f"Output file {self.output_path} was not created.")

    def resize_video(self, resolution):
        import subprocess
        import os

        # Define common resolution presets
        resolutions = {
            '480p': (854, 480),
            '720p': (1280, 720),
            '1080p': (1920, 1080)
        }

        # Get the dimensions for the requested resolution
        if resolution not in resolutions:
            raise ValueError(f"Unsupported resolution: {resolution}")
        width, height = resolutions[resolution]

        # Generate output path based on input path
        output_dir, input_filename = os.path.split(self.input_path)
        output_filename = f'resized_{resolution}_{input_filename}'
        self.output_path = os.path.join(output_dir, output_filename)
        
        # Check if the output file already exists and overwrite it
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

        # ffmpeg command to resize the video
        command = [
            self.ffmpeg_path,
            '-i', self.input_path,
            '-vf', f'scale={width}:{height}',
            '-c:a', 'copy',
            self.output_path
        ]
        subprocess.run(command, check=True)

        # Check if the output file was created
        if not os.path.exists(self.output_path):
            raise FileNotFoundError(f"Output file {self.output_path} was not created.")

        return self.output_path

####### Read the config file to get the user inputs ########
config = configparser.ConfigParser()
config.sections()
config.read('config.ini')
settings = config['VideoSettings']
input_path = settings['input_path']
ffmpeg_path = settings['ffmpeg_path']
cut_video = settings['cut_video']
start_time = settings['start_time']
duration = settings['duration']
keep_audio = settings['keep_audio']
resize_video = settings.getboolean('resize_video')  # Read as boolean
resolution = settings['resolution']  # Read resolution

blur = config['Blurring']
confidence_threshold = float(blur['threshold'])

mod = config['ModelSettings']
model_name = mod['yolo_model']


video_path = input_path

###### THIS IS THE START OF THE PROGRAM #######
print("\n\nLoading video... \n\n")

if cut_video == 'true':
    print("Cutting video...\n")
    cutter = VideoCutter(video_path, ffmpeg_path)
    cutter.cut_video(int(start_time), int(duration))
    video_path = cutter.output_path
    
    print("\nThe video was successfully cut.\n")

# Check if resize_video is true and call resize_video method
if resize_video:
    print(f"Resizing video to {resolution}...")
    cutter = VideoCutter(video_path, ffmpeg_path)
    video_path = cutter.resize_video(resolution)
    print("Video resized successfully.")

# YOLO model
model = YOLO(model_name)

# Create a VideoCapture object
cap = cv2.VideoCapture(video_path)
file_size = os.path.getsize(video_path)  # Get file size in bytes

# Check if the video opened successfully
if not cap.isOpened():
    print("Error: Invalid path, could not open video.")
    exit()

# Get the width and height of the frames
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
time_per_frame_face = TIME_PER_FRAME_FACE
time_per_frame_head = TIME_PER_FRAME_HEAD
fps = int(cap.get(cv2.CAP_PROP_FPS))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Ensure this is after reinitializing cap
print(f"File size: {os.path.getsize(video_path) * 0.001} kB")
print(f"Total frames in the video: {total_frames}")

if model_name=='YOLOv8n-face.pt':
    print(f"Estimated time is {round(time_per_frame_face * total_frames, 2)} minutes")
elif model_name=='best_re_final.pt':
    print(f"Estimated time is {round(time_per_frame_head * total_frames, 2)} minutes")
else:
    print("Model name does not match a known choice...")
    print("Terminating the program...")
    exit()


# Ask user if they want to continue
# Clear any previous output before asking for input
print("\n")  # Optional: Add a newline for clarity
user_input = input("Tap 'Enter' three times to accept or exit the program").strip().lower()
if user_input != '':
    print("Exiting the program.")
    exit()
else: 
    print("\nInitializing inference...\n")


# Generate output path based on input path
video_output_dir, video_filename = os.path.split(video_path)
video_filename = 'blurred_' + video_filename

# Check if the video filename already exists, in that case, remove it
if os.path.exists(os.path.join(video_output_dir, video_filename)):
    os.remove(os.path.join(video_output_dir, video_filename))

# Create the new video path
video_output_path = os.path.join(video_output_dir, video_filename)


# Define the codec and create a VideoWriter object
out = cv2.VideoWriter(video_output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

# Define the class you want to filter (e.g., class 0)
desired_class = 0

# Create a buffer to store bounding boxes for consecutive frames
bbox_buffer = []

# Initialize a variable to store the start time
start_time = time.time()

# Read until the video is completed
while cap.isOpened():
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    if ret:
        # Process the frame with YOLO model in streaming mode with confidence threshold
        results = model(frame, stream=True, conf=confidence_threshold)
        
        # Store current frame's bounding boxes
        current_bboxes = []
        for result in results:
            for box in result.boxes:
                if box.cls == desired_class:  # Filter by desired class
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    current_bboxes.append((x1, y1, x2, y2))
        
        # Add current frame's bounding boxes to the buffer
        bbox_buffer.append(current_bboxes)
        
        # Keep only the last 3 frames in the buffer
        if len(bbox_buffer) > 3:
            bbox_buffer.pop(0)
        
        # Apply blur to bounding boxes from the buffer
        for bboxes in bbox_buffer:
            for (x1, y1, x2, y2) in bboxes:
                # Scale the bounding box dimensions by 1.2
                scale_factor = 1.6
                new_width = int((x2 - x1) * scale_factor)
                new_height = int((y2 - y1) * scale_factor)
                new_x1 = max(0, x1 - (new_width - (x2 - x1)) // 2)
                new_y1 = max(0, y1 - (new_height - (y2 - y1)) // 2)
                new_x2 = min(frame.shape[1], new_x1 + new_width)
                new_y2 = min(frame.shape[0], new_y1 + new_height)
                bbox = (new_x1, new_y1, new_x2 - new_x1, new_y2 - new_y1)
                
                # Extract the region of interest (ROI)
                roi = frame[new_y1:new_y2, new_x1:new_x2]
                
                # Calculate the kernel size based on the bounding box size
                kernel_size = max(51, int(min(bbox[2], bbox[3]) / 10) * 2 + 1)
                
                # Apply gaussian blur to the ROI
                blurred_roi = cv2.GaussianBlur(roi, (kernel_size, kernel_size), 0)
                
                # Create a mask for the ellipse
                mask = np.zeros_like(roi)
                center = (bbox[2] // 2, bbox[3] // 2)
                axes = (bbox[2] // 2, bbox[3] // 2)
                cv2.ellipse(mask, center, axes, 0, 0, 360, (255, 255, 255), -1)
                
                # Combine the blurred ROI with the original frame using the mask
                frame[new_y1:new_y2, new_x1:new_x2] = np.where(mask == 255, blurred_roi, roi)
        
        # Write the frame into the output video
        out.write(frame)
        
        # Press Q on keyboard to exit or close the window
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    else:
        break

# When everything done, release the video capture and writer objects
cap.release()
out.release()



# Closes all the frames
cv2.destroyAllWindows()

if keep_audio == 'true':
    print("\nExtracting the audio from the original video...\n")

    # Generate output path based on input path
    audio_dir, audio_filename = os.path.split(video_path)
    audio_filename = 'w_audio_' + os.path.basename(video_output_path)  # Use basename of video_output_path

    # Check if the audio filename already exists, in that case, remove it
    if os.path.exists(os.path.join(audio_dir, audio_filename)):
        os.remove(os.path.join(audio_dir, audio_filename))

    # Create the new audio output path
    video_audio_output_path = os.path.join(audio_dir, audio_filename)

    # Extract audio from the original video
    audio_output_path = 'audio.aac'  # Temporary audio file
    subprocess.run([ffmpeg_path, '-i', video_path, '-q:a', '0', '-map', 'a', audio_output_path])

    # Combine the processed video with the original audio
    output_video_with_audio = os.path.join(audio_dir, video_audio_output_path)  # Define the output path
    subprocess.run([ffmpeg_path, '-i', video_path, '-i', audio_output_path, '-c:v', 'copy', '-c:a', 'aac', output_video_with_audio])

    # Clean up temporary audio file
    os.remove(audio_output_path)

    # Calculate the elapsed time
    elapsed_time = time.time() - start_time
    print("\n\n#######################################\n\n")
    print("\n\nFinished processing video...\n")
    print("Saving the output files to the same folder as the input video...")
    print(f"Elapsed time: {elapsed_time/60} minutes")
    print(f"\nOutput file with audio saved as: {output_video_with_audio}\n")

else:
    # Calculate the elapsed time
    elapsed_time = time.time() - start_time
    print("\n\nFinished blurring video...\n")
    print("Saving the output file to the same folder as the input video...")
    print(f"Output file name: {video_output_path}")
    print(f"Elapsed time: {elapsed_time/60} minutes\n")

# Closes all the frames
cv2.destroyAllWindows()

# Add this line to pause the console
input("Press 'Enter' to exit the program... ")  # This will keep the console open until you press Enter
