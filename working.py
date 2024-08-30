####################
# File Name: working.py
# Author: Philiph Lundberg
# Date Created: 2024-08
# Description: This script processes video files by cutting, resizing, and applying blurring effects using YOLO model.
# Version: 1.0
# License: MIT License
####################



import cv2
from ultralytics import YOLO
import numpy as np
import time
import configparser
import os
import subprocess
# from win10toast import ToastNotifier
import tkinter as tk
from tkinter import font as tkFont
import ctypes
from ctypes import wintypes
import winsound



TIME_PER_FRAME_FACE = 0.0031355378818845 #minutes
TIME_PER_FRAME_HEAD = 0.02867874396 #minutes
TIME_PER_FRAME_FACE2 = 0.030292887 #minutes

FLASHW_STOP = 0
FLASHW_CAPTION = 0x00000001
FLASHW_TRAY = 0x00000002
FLASHW_ALL = 0x00000003
FLASHW_TIMER = 0x00000004
FLASHW_TIMERNOFG = 0x0000000C


class VideoCutter:
    def __init__(self, input_path, ffmpeg_path='ffmpeg'):
        self.input_path = input_path
        self.ffmpeg_path = ffmpeg_path

    def cut_video(self, start_time, end_time):
        # Convert MM:SS to seconds
        start_time = self.convert_to_seconds(start_time)
        end_time = self.convert_to_seconds(end_time)
        duration = end_time - start_time  # Calculate duration

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
            '-ss', str(start_time),  # Start time     
            '-i', self.input_path,   # Input file
            '-t', str(duration),     # Duration
            '-c:v', 'copy',          # Copy video codec (no re-encoding)
            '-c:a', 'copy',          # Copy audio codec (no re-encoding)
            self.output_path         # Output file
        ]
        subprocess.run(command, check=True)

        # Check if the output file was created
        if not os.path.exists(self.output_path):
            raise FileNotFoundError(f"Output file {self.output_path} was not created.")

    def convert_to_seconds(self, time_str):
        """Convert MM:SS format to seconds."""
        minutes, seconds = map(int, time_str.split(':'))
        return minutes * 60 + seconds

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
    
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
user32 = ctypes.WinDLL('user32', use_last_error=True)

def play_notification_sound():
    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

class FLASHWINFO(ctypes.Structure):
    _fields_ = (('cbSize', wintypes.UINT),
                ('hwnd', wintypes.HWND),
                ('dwFlags', wintypes.DWORD),
                ('uCount', wintypes.UINT),
                ('dwTimeout', wintypes.DWORD))
    def __init__(self, hwnd, flags=FLASHW_TRAY, count=5, timeout_ms=0):
        self.cbSize = ctypes.sizeof(self)
        self.hwnd = hwnd
        self.dwFlags = flags
        self.uCount = count
        self.dwTimeout = timeout_ms

kernel32.GetConsoleWindow.restype = wintypes.HWND
user32.FlashWindowEx.argtypes = (ctypes.POINTER(FLASHWINFO),)

def flash_console_icon(count=5):
    hwnd = kernel32.GetConsoleWindow()
    if not hwnd:
        raise ctypes.WinError(ctypes.get_last_error())
    winfo = FLASHWINFO(hwnd, count=count)
    previous_state = user32.FlashWindowEx(ctypes.byref(winfo))
    return previous_state

####### Read the config file to get the user inputs ########
config = configparser.ConfigParser()
config.sections()
config.read('config.ini')
settings = config['VideoSettings']
input_path = settings['input_path']
ffmpeg_path = settings['ffmpeg_path']
cut_video = settings['cut_video']
start_time = settings['start_time']  # Read as MM:SS
end_time = settings['duration']  # Read as MM:SS
keep_audio = settings['keep_audio']
resize_video = settings.getboolean('resize_video')  # Read as boolean
resolution = settings['resolution']  # Read resolution

blur = config['Blurring']
confidence_threshold = float(blur['threshold'])

mod = config['ModelSettings']
model_name = mod['yolo_model']

# Used to override to try custom videos
video_path = input_path

###### THIS IS THE START OF THE PROGRAM #######
print("\n\nLoading video... \n\n")

if cut_video == 'true':
    print("Cutting video...\n")
    cutter = VideoCutter(video_path, ffmpeg_path)
    cutter.cut_video(start_time, end_time)  # Pass start_time and end_time
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
time_per_frame_face2 = TIME_PER_FRAME_FACE2
fps = int(cap.get(cv2.CAP_PROP_FPS))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Ensure this is after reinitializing cap
print(f"File size: {os.path.getsize(video_path) * 0.001} kB")
print(f"Total frames in the video: {total_frames}")

# Define a mapping of model names to their respective time calculations
model_time_estimations = {
    'YOLOv8n-face.pt': (time_per_frame_face, 'minutes'),
    'yolov8m-face.pt': (time_per_frame_face2, 'minutes'),
    'best_re_final.pt': (time_per_frame_head, 'minutes'),
    'yolov8s.pt': (time_per_frame_head, 'minutes')
}

# Get the time per frame and unit based on the model name
time_per_frame, unit = model_time_estimations.get(model_name, (None, None))

if time_per_frame is not None:
    estimated_time = round(time_per_frame * total_frames, 2)
    if estimated_time > 120:
        print(f"Estimated time is {round(estimated_time / 60, 1)} hours")
    else:
        print(f"Estimated time is {estimated_time} minutes")
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
elapsed_start_time = time.time()

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
                # Scale the bounding box dimensions
                if model_name == "yolov8s.pt":
                    scale_factor = 1.0
                else:
                    scale_factor = 1.6
                new_width = int((x2 - x1) * scale_factor)
                new_height = int((y2 - y1) * scale_factor)

                # Ensure new_width and new_height are positive
                if new_width <= 0 or new_height <= 0:
                    continue  # Skip this bounding box if dimensions are invalid

                new_x1 = max(0, x1 - (new_width - (x2 - x1)) // 2)
                new_y1 = max(0, y1 - (new_height - (y2 - y1)) // 2)
                new_x2 = min(frame.shape[1], new_x1 + new_width)
                new_y2 = min(frame.shape[0], new_y1 + new_height)
                bbox = (new_x1, new_y1, new_x2 - new_x1, new_y2 - new_y1)
                
                # Extract the region of interest (ROI)
                roi = frame[new_y1:new_y2, new_x1:new_x2]
                
                # Calculate the kernel size based on the bounding box size
                kernel_size = int(max(51, int(min(bbox[2], bbox[3]) / 10) * 4 + 1))
                
                # Apply gaussian blur to the ROI
                blurred_roi = cv2.GaussianBlur(roi, (kernel_size, kernel_size), 0)

                if model_name == "yolov8s.pt":
                    # Apply blur to the entire bounding box region
                    frame[new_y1:new_y2, new_x1:new_x2] = blurred_roi
                elif model_name == "head accurate":
                    # Apply Box blur
                    # kernel_size = 2 * int(max(51, int(min(bbox[2], bbox[3]) / 10) * 4 + 1))
                    kernel_size = (51,51)
                    blurred_roi = cv2.blur(roi, (kernel_size, kernel_size))
                    frame[new_y1:new_y2, new_x1:new_x2] = blurred_roi
                else:
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
    elapsed_time = time.time() - elapsed_start_time
    print("\n\n#######################################\n\n")
    print("\n\nFinished processing video...\n")
    print("Saving the output files to the same folder as the input video...")
    print(f"Elapsed time: {round(elapsed_time/60, 2)} minutes")
    print(f"\nOutput file with audio saved as: {os.path.basename(output_video_with_audio)}\n")

else:
    # Calculate the elapsed time
    elapsed_time = time.time() - elapsed_start_time
    print("\n\nFinished blurring video...\n")
    print("Saving the output file to the same folder as the input video...")
    print(f"Output file name: {os.path.basename(video_output_path)}")
    if elapsed_time/60 > 120:
        print(f"Elapsed time: {round(elapsed_time/(60*60), 2)} hours")
    else:
        print(f"Elapsed time: {round(elapsed_time/60, 2)} minutes\n")

# Closes all the frames
cv2.destroyAllWindows()

# After the video processing is completed
# toast = ToastNotifier()
# toast.show_toast("Video Processing", "Processing completed successfully!", duration=10, threaded=True)

flash_console_icon(count=10)
play_notification_sound()  # Play a notification sound (optional)

# Add this line to pause the console
input("Press 'Enter' to exit the program... ")  # This will keep the console open until you press Enter
