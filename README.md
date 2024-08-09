# Video Cutter and Blurrer

## Overview
This Python script allows users to cut a video and apply a blurring effect to specific objects detected using the YOLO (You Only Look Once) model. In my project I used a model trained to identify faces to automatically blur them. It also provides an option to extract and retain audio from the original video.

## Acknowledgements
This project uses the Ultralytics YOLO model. Please refer to the [Ultralytics YOLO repository](https://github.com/ultralytics/ultralytics) for more information and its licensing terms.


## Requirements
- Python 3.x
- OpenCV
- Ultralytics
- FFmpeg
- NumPy
- ConfigParser

## Installation
1. Install Python
	- In the FaceBlurAI folder you can find a python executable named "python-3.12.5-amd64.exe"
	- Run it by double pressing
	- When the first dialog pops up, make sure you tick the "Add python.exe to PATH" at the bottom and click "Install Now"
		NOTE: Since we can't manually go into the systems environment variables and add the PATH, if you forget to tick the box, you need to uninstall Python and start over.
		      The same happens if you have installed python and then move the folder or python.exe, then you need to reinstall as well
	- When the installation is successful, you can close the window

2.1 Install FaceBlurAI
	- Double tap the FaceBlurAI_installer.py file
	- This will open the Python Launcher which starts the package downloading
	- Wait for all things to install
	- The launcher will close when everything is installed

3. Create shortcut
	- Drag the "FaceBlurAI"-file to the desktop to get your own shortcut

## Uninstall
1. Uninstall Python
	- Go to the search bar and search for "Appar och funktioner"
	- Type "Python" in the search bar or scroll until you see it
	- There should be two python-files, uninstall both
2. Uninstall FaceBlurAI
	- Double tap the file called "uninstaller"

## Usage
1. Run the script:
	- The FaceBlurAI shortcut is just a shortcut to run.bat with a fancy name and icon
		The run.bat file is the base file used to run the program
		This shortcut is created to ensure that nothing happens to the original file
	- Double tap FaceBlurAI to open the program.
2. Use the program:
	- Two things will pop up: The User Interface (UI) and the console
		The UI is used to configure the settings
		The console will give some output messages to keep track of where you are in the script
	- In the UI you first select the wanted video by copying the path to the video and ending with the video name
		Make sure you include the file type (.MP4 usually)
	- You can also specify if you want to cut the video into a smaller video
		You do this by first ticking the box that says cut and press "Save Configurations"
		Two other boxes will then appear where you specify the new start time (in seconds) of the video and how long you want the video to be
		NOTE: The "Duration" input is the LENGTH of the video in seconds, not the end time
		Make sure that you press "Save Configurations" again after you set the times, otherwise it won't update the settings
	- The slider that says "Confidence" signifies how certain you want the AI to be that it is a face.
		Pro of having a high confidence: The AI will not blur things that isn't a face, for example: the AI sometimes blurres chairs for no apparent reason
		Con of having a high confidence: The AI will sometimes miss faces and not blur them
		I found a good balance by having the confidence of 30% which is the default
	- When you are satisfied with the settings, press "Save Configurations" a final time before pressing "Run Blurring Script"
		This will cause the program to close the UI and switch to the console
   
2. Using the console: 
	- The program will start using your desired settings
		You will see different messages based on your settings
	- Before the AI starts working on blurring the video it will give you some information about the video
		This includes file size and an approximated runtime for the script
	- You will be asked to press 'Enter' three times to proceed with the video processing.
	- The inference will start and you can minimize the window
	- When the script has stopped running, you will see a summary including actual runtime and the path to the output video

## Features
- **Cut Video**: The script can cut a specified portion of the video based on the start time and duration.
- **Blur Objects**: It applies a Gaussian blur to detected objects of a specified class in the video. (Faces in my case)
- **Audio Extraction**: Optionally retains the original audio in the output video. Default is to remove the audio because of swedish privacy regulations.

## Output
- The processed video will be saved in the same directory as the input video, with the following naming conventions:
  - Cut video: `cut_<original_filename>`
  - Blurred video: `blurred_<original_filename>`
  - Audio (if kept): `w_audio_<blurred_filename>`

## Configuration (This is included for Komatsu employees)
Create a 'config.ini' file in the same directory as the script with the following structure (if the file does not exist):

[VideoSettings]
input_path = path/to/your/video.mp4
ffmpeg_path = path/to/ffmpeg
cut_video = true
start_time = 0 # Start time in seconds
duration = 10 # Duration in seconds
keep_audio = true # Set to 'true' to keep audio
[Blurring]
threshold = 0.5 # Confidence threshold for object detection

## Notes
- Ensure that the YOLO model file (`yolov8n-face.pt`) is available in the same directory or provide the correct path in the script.
- Adjust the `desired_class` variable in the script to target different object classes for blurring.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
