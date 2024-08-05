# FaceBlurAI

## Overview
This Python script allows users to cut a video and apply a blurring effect to specific objects detected using the YOLO (You Only Look Once) model. In my projrct I used a model trained to identify faces to automatically blur them. It also provides an option to extract and retain audio from the original video.

## Acknowledgements
This project uses the Ultralytics YOLO model. Please refer to the [Ultralytics YOLO repository](https://github.com/ultralytics/ultralytics) for more information and its licensing terms.

## Requirements
- Python 3.x
- OpenCV
- Ultralytics YOLO
- FFmpeg
- NumPy
- ConfigParser

## Installation
1. Install the required libraries:
   ```bash
   pip install opencv-python ultralytics numpy
   ```
2. Ensure FFmpeg is installed and accessible in your system's PATH.

## Configuration
Create a `config.ini` file in the same directory as the script with the following structure:

[VideoSettings]
input_path = path/to/your/video.mp4
ffmpeg_path = path/to/ffmpeg
cut_video = true
start_time = 0 # Start time in seconds
duration = 10 # Duration in seconds
keep_audio = true # Set to 'true' to keep audio
[Blurring]
threshold = 0.5 # Confidence threshold for object detection

## Usage
1. Run the script:
   The run.bat file is used to run the program which starts the GUI
2. Follow the prompts in the console. You will be asked to press 'Enter' three times to proceed with the video processing.

## Features
- **Cut Video**: The script can cut a specified portion of the video based on the start time and duration.
- **Blur Objects**: It applies a Gaussian blur to detected objects of a specified class in the video. (Faces in my case)
- **Audio Extraction**: Optionally retains the original audio in the output video. Default is to remove the audio because of swedish privacy regulations.

## Output
- The processed video will be saved in the same directory as the input video, with the following naming conventions:
  - Cut video: `cut_<original_filename>`
  - Blurred video: `blurred_<original_filename>`
  - Audio (if kept): `w_audio_<blurred_filename>`

## Notes
- Ensure that the YOLO model file (`yolov8n-face.pt`) is available in the same directory or provide the correct path in the script.
- Adjust the `desired_class` variable in the script to target different object classes for blurring.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
