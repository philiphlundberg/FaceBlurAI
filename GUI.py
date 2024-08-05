# Project Name: FaceBlurAI
# License: MIT
# Author: Philiph Lundberg
# Date: 2024-08-05

import tkinter as tk
from tkinter import filedialog
import configparser
import subprocess  # Add this import


#### GUI FOR THE FACEBLUR AI PROGRAM ####

# Add a global flag to track if the input start entry has been created
input_start_created = False
input_duration_created = False

def save_config():
    global input_start_created, input_duration_created # Declare both as global
    config['VideoSettings']['input_path'] = input_path_entry.get()
    config['Blurring']['threshold'] = str(value_slider.get())

    if keep_audio_var.get():
        config['VideoSettings']['keep_audio'] = 'true'
    else:
        config['VideoSettings']['keep_audio'] = 'false'

    if cut_video_var.get():
        config['VideoSettings']['cut_video'] = 'true'
        
        # Check if the input_start_label already exists
        if not input_start_created:  # Use the flag to check
            global input_start_label, input_start_entry  # Declare as global to modify outside the function
            input_start_label = tk.Label(root, text="Start time of video:", bg='lightblue', fg='black')  # Customize colors
            input_start_label.pack()
            input_start_entry = tk.Entry(root, width=50, bg='white', fg='black')  # Customize colors
            input_start_entry.insert(0, config['VideoSettings']['start_time'])
            input_start_entry.pack()
            input_start_created = True  # Set the flag to True after creation

        # Check if the input_start_label already exists
        if not input_duration_created:  # Use the flag to check
            global input_duration_label, input_duration_entry  # Declare as global to modify outside the function
            input_duration_label = tk.Label(root, text="Duration:", bg='lightblue', fg='black')  # Customize colors
            input_duration_label.pack()
            input_duration_entry = tk.Entry(root, width=50, bg='white', fg='black')  # Customize colors
            input_duration_entry.insert(0, config['VideoSettings']['duration'])
            input_duration_entry.pack()
            input_duration_created = True  # Set the flag to True after creation
        
        config['VideoSettings']['start_time'] = input_start_entry.get()
        config['VideoSettings']['duration'] = input_duration_entry.get()
    else:
        config['VideoSettings']['cut_video'] = 'false'
    
    
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def start_other_script():  
    subprocess.Popen(['python', 'working.py'])  # Replace 'working.py' with your file name
    root.destroy()  # Close the config editor GUI

# Load config file
config = configparser.ConfigParser()
config.read('config.ini')

# Create GUI
root = tk.Tk()
root.title("FaceBlur")
root.geometry("500x400")  # Set the window size to 400x300 pixels
root.configure(bg='lightblue')  # Set background color for the main window

input_path_label = tk.Label(root, text="Path to video:", bg='lightblue', fg='black')  # Customize colors
input_path_label.pack()
input_path_entry = tk.Entry(root, width=50, bg='white', fg='black')  # Customize colors
input_path_entry.insert(0, config['VideoSettings']['input_path'])
input_path_entry.pack()

# Frame for Cut Video
cut_video_frame = tk.Frame(root, bg='lightblue')  # Create a frame for cut video
cut_video_frame.pack(side=tk.LEFT, padx=50)  # Align to the left with padding
cut_video_label = tk.Label(cut_video_frame, text="Cut video:", bg='lightblue', fg='black')  # Customize colors
cut_video_label.pack(pady=5)  # Pack label with vertical padding
cut_video_var = tk.BooleanVar(root)
cut_video_var.set(config['VideoSettings'].getboolean('cut_video'))
cut_video_checkbox = tk.Checkbutton(cut_video_frame, text="Yes", variable=cut_video_var, bg='lightblue', fg='black')  # Customize colors
cut_video_checkbox.pack(pady=5)  # Pack checkbox with vertical padding

keep_audio_frame = tk.Frame(root, bg='lightblue')  # Create a frame for cut video
keep_audio_frame.pack(side=tk.RIGHT, padx=50)  # Align to the right with padding
keep_audio_label = tk.Label(keep_audio_frame, text="Keep audio:", bg='lightblue', fg='black')  # Customize colors
keep_audio_label.pack(pady=5)  # Pack label with vertical padding
keep_audio_var = tk.BooleanVar(root)
keep_audio_var.set(config['VideoSettings'].getboolean('keep_audio'))
keep_audio_checkbox = tk.Checkbutton(keep_audio_frame, text="Yes", variable=keep_audio_var, bg='lightblue', fg='black')  # Customize colors
keep_audio_checkbox.pack(pady=5)  # Pack checkbox with vertical padding

slider_label = tk.Label(root, text="Set Confidence Level:", bg='lightblue', fg='black')  # Customize colors
slider_label.pack()
value_slider = tk.Scale(root, from_=0.0, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, bg='lightblue', fg='black')  # Customize colors
value_slider.set(0.3)  # Set default value to 0.3
value_slider.pack()

# Positioning buttons using place()
save_button = tk.Button(root, text="Save Configurations", command=save_config, bg='green', fg='white')  # Customize colors
save_button.place(x=90, y=300)  # Set x and y coordinates

start_button = tk.Button(root, text="Run Blurring Script", command=start_other_script, bg='blue', fg='white')  # Customize colors
start_button.place(x=300, y=300)  # Set x and y coordinates

root.mainloop()
