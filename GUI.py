####################
# File Name: GUI.py
# Author: Philiph Lundberg
# Date Created: 2024-08
# Description: This script is responsible for the GUI of FaceBlurAI
# Version: 1.0
# License: MIT License
####################


import tkinter as tk
from tkinter import filedialog
import configparser
import subprocess  # Add this import
import tkinter as tk
from tkinter import font as tkfont
from tkinter import StringVar
from PIL import Image, ImageTk  # Add this import
from tkinter import ttk  # Add this import for the dropdown menu

#### GUI FOR THE FACEBLUR AI PROGRAM ####

# Add a global flag to track if the input start entry has been created
input_start_created = False
input_duration_created = False

# Slightly darker light grey color scheme
bg_color = '#e0e0e0'  # Slightly darker light grey for background
fg_color = '#333333'  # Dark grey for text
button_bg = '#4a86e8'  # Blue for buttons
button_fg = '#ffffff'  # White text for buttons
entry_bg = '#f5f5f5'  # Very light grey for input fields
entry_fg = '#333333'  # Dark grey text for input fields
switch_bg = '#c0c0c0'  # Medium grey for switch background
switch_fg = '#0c039b'  # Blue for switch foreground
accent_color = '#34a853'  # Green accent color for highlights or important elements

def save_config():
    global input_start_created, input_duration_created  # Declare both as global
    
    config['VideoSettings']['input_path'] = input_path_entry.get()
    config['Blurring']['threshold'] = str(value_slider.get())
    
    # Ensure ModelSettings section exists
    if 'ModelSettings' not in config:
        config['ModelSettings'] = {}
    
    # Get the display name from the dropdown
    selected_display_name = model_var.get()
    
    # Map the display name to the actual model filename
    selected_model_filename = model_mapping.get(selected_display_name)
    
    # DEBUG: Print to confirm the correct model filename is being saved
    # print(f"Saving model to config: {selected_model_filename}")
    
    # Save the selected model filename to the config
    if selected_model_filename:
        config['ModelSettings']['yolo_model'] = selected_model_filename
    else:
        print(f"Error: Selected display name '{selected_display_name}' has no corresponding model filename.")
    
    # Save the selected resolution
    config['VideoSettings']['resize_video'] = str(change_res_var.get())  # Convert to string
    config['VideoSettings']['resolution'] = res_var.get()  # Save the selected resolution

    if keep_audio_var.get():
        config['VideoSettings']['keep_audio'] = 'true'
    else:
        config['VideoSettings']['keep_audio'] = 'false'

    if cut_video_var.get():
        config['VideoSettings']['cut_video'] = 'true'
        
        # Check if the input_start_label already exists
        if not input_start_created:  # Use the flag to check
            global input_start_label, input_start_entry  # Declare as global to modify outside the function
            tk.Label(root, text="", bg=bg_color, height=2).pack()  # Adjust height as needed
            input_start_label = tk.Label(root, text="Start time of video [MM:SS]:", bg=bg_color, fg=fg_color)  # Customize colors
            input_start_label.pack()
            input_start_entry = tk.Entry(root, width=50, bg=entry_bg, fg=entry_fg)  # Customize colors
            input_start_entry.insert(0, config['VideoSettings']['start_time'])
            input_start_entry.pack()
            input_start_created = True  # Set the flag to True after creation

        if not input_duration_created:  # Use the flag to check
            global input_duration_label, input_duration_entry  # Declare as global to modify outside the function
            input_duration_label = tk.Label(root, text="End time of video [MM:SS]:", bg=bg_color, fg=fg_color)  # Customize colors
            input_duration_label.pack()
            input_duration_entry = tk.Entry(root, width=50, bg=entry_bg, fg=entry_fg)  # Customize colors
            input_duration_entry.insert(0, config['VideoSettings']['duration'])
            input_duration_entry.pack()
            input_duration_created = True  # Set the flag to True after creation
        
        config['VideoSettings']['start_time'] = input_start_entry.get()
        config['VideoSettings']['duration'] = input_duration_entry.get()
    else:
        config['VideoSettings']['cut_video'] = 'false'
    
    # Write the configuration to the file
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
root.title("FaceBlurAI")
root.geometry("500x750")  # Set the window size to 500x750 pixels
root.configure(bg=bg_color)  # Set background color for the main window

# Add logo
logo_image = Image.open(r"W:\Umea\PT\Media\11. Balansering\FaceBlurAI\Komatsu_logo.png")  # Replace with your logo file path
logo_image = logo_image.resize((200, 40))  # Adjust size as needed
logo_photo = ImageTk.PhotoImage(logo_image)
logo_label = tk.Label(root, image=logo_photo, bg=bg_color)
logo_label.image = logo_photo  # Keep a reference
logo_label.pack(pady=10)  # Adjust padding as needed
# Add logo
slogan_image = Image.open(r"W:\Umea\PT\Media\11. Balansering\FaceBlurAI\Brand_slogan.png")  # Replace with your logo file path
slogan_image = slogan_image.resize((100, 20))  # Adjust size as needed
slogan_photo = ImageTk.PhotoImage(slogan_image)
slogan_label = tk.Label(root, image=slogan_photo, bg=bg_color)
slogan_label.image = slogan_photo  # Keep a reference
slogan_label.place(x=350, y=34)# (x=150, y=52)  # Adjust position of slogan

# Add this line to create vertical space
tk.Label(root, text="", bg=bg_color, height=2).pack()  # Adjust height as needed

# Create a frame to hold the input path entry and browse button
input_frame = tk.Frame(root, bg=bg_color)
input_frame.pack(pady=10)  # Adjust padding as needed

def browse_file():
    file_path = filedialog.askopenfilename()  # Open file dialog to select a file
    input_path_entry.delete(0, tk.END)  # Clear the current entry
    input_path_entry.insert(0, file_path)  # Insert the selected file path

# Change the label text and position
input_path_label = tk.Label(input_frame, text="Choose video:", bg=bg_color, fg=fg_color)  # Updated text
input_path_label.grid(row=0, column=0, sticky='w', columnspan=2)  # Label spans two columns

# Create the input path entry before the label
input_path_entry = tk.Entry(input_frame, width=50, bg=entry_bg, fg=entry_fg)  # Customize colors
input_path_entry.insert(0, config['VideoSettings']['input_path'])  # Initialize with config value
input_path_entry.grid(row=1, column=0, padx=(0, 5))  # Entry in the second row

# Add the browse button to the same frame
browse_button = tk.Button(input_frame, text="Browse", command=browse_file, bg=button_bg, fg=button_fg)
browse_button.grid(row=1, column=1)  # Button in the second column of the same row

# Create a frame to hold both Cut Video and Change Resolution options
options_frame = tk.Frame(root, bg=bg_color)
options_frame.pack(pady=10)

# Frame for Cut Video
cut_video_frame = tk.Frame(options_frame, bg=bg_color)
cut_video_frame.grid(row=0, column=0, padx=20, pady=5, sticky='w')
cut_video_label = tk.Label(cut_video_frame, text="Cut video:", bg=bg_color, fg=fg_color)
cut_video_label.grid(row=0, column=0, sticky='w')
cut_video_var = tk.BooleanVar(root)
cut_video_var.set(config['VideoSettings'].getboolean('cut_video'))
cut_video_checkbox = tk.Checkbutton(cut_video_frame, text="Yes", variable=cut_video_var, bg=bg_color, fg=fg_color, selectcolor=switch_bg)
cut_video_checkbox.grid(row=1, column=0, sticky='w')

# Frame for Change Resolution
change_res_frame = tk.Frame(options_frame, bg=bg_color)
change_res_frame.grid(row=0, column=1, padx=20, pady=5, sticky='w')
change_res_label = tk.Label(change_res_frame, text="Change resolution:", bg=bg_color, fg=fg_color)
change_res_label.grid(row=0, column=0, sticky='w')
change_res_var = tk.BooleanVar(root)
change_res_var.set(False)  # Set default to False (unchecked)
change_res_checkbox = tk.Checkbutton(change_res_frame, text="Yes", variable=change_res_var, bg=bg_color, fg=fg_color, selectcolor=switch_bg, command=lambda: toggle_resolution_options())
change_res_checkbox.grid(row=1, column=0, sticky='w')

# Frame for Resolution Options (moved to the right of Change Resolution)
res_options_frame = tk.Frame(change_res_frame, bg=bg_color)
res_options_frame.grid(row=2, column=0, sticky='w')  # Adjusted to be below the checkbox
res_var = tk.StringVar(value=config['VideoSettings'].get('resolution', '720p'))
res_480 = tk.Radiobutton(res_options_frame, text="480p", variable=res_var, value="480p", bg=bg_color, fg=fg_color, selectcolor=switch_bg)
res_720 = tk.Radiobutton(res_options_frame, text="720p", variable=res_var, value="720p", bg=bg_color, fg=fg_color, selectcolor=switch_bg)
res_1080 = tk.Radiobutton(res_options_frame, text="1080p", variable=res_var, value="1080p", bg=bg_color, fg=fg_color, selectcolor=switch_bg)

def toggle_resolution_options():
    if change_res_var.get():
        res_480.grid(row=0, column=0, sticky='w')
        res_720.grid(row=1, column=0, sticky='w')
        res_1080.grid(row=2, column=0, sticky='w')
    else:
        res_480.grid_remove()
        res_720.grid_remove()
        res_1080.grid_remove()

# Initial state of resolution options
toggle_resolution_options()

# Frame for Keep Audio
keep_audio_frame = tk.Frame(options_frame, bg=bg_color)  # Create a frame for keep audio
keep_audio_frame.grid(row=0, column=2, padx=20, pady=5, sticky='w')  # Align to the right with padding
keep_audio_label = tk.Label(keep_audio_frame, text="Keep audio:", bg=bg_color, fg=fg_color)  # Customize colors
keep_audio_label.grid(row=0, column=0, sticky='w')  # Pack label with vertical padding
keep_audio_var = tk.BooleanVar(root)
keep_audio_var.set(False)  # Set default to False (unchecked)
keep_audio_checkbox = tk.Checkbutton(keep_audio_frame, text="Yes", variable=keep_audio_var, bg=bg_color, fg=fg_color, selectcolor=switch_bg)  # Customize colors
keep_audio_checkbox.grid(row=1, column=0, sticky='w')  # Pack checkbox with vertical padding

# Frame for YOLO model selection
yolo_model_frame = tk.Frame(root, bg=bg_color)
yolo_model_frame.pack(pady=10)

yolo_model_label = tk.Label(yolo_model_frame, text="Blurring model:", bg=bg_color, fg=fg_color)
yolo_model_label.pack()

# Create a dictionary to map display names to model filenames
model_mapping = {
    "Face Fast": "YOLOv8n-face.pt",
    "Face Accurate": "yolov8m-face.pt",
    "Head Accurate": "best_re_final.pt",
    "Person Accurate": "yolov8s.pt"
}

# Get the display names (keys of the dictionary) for the dropdown
model_display_names = list(model_mapping.keys())

# Set up the StringVar with a default value
model_var = tk.StringVar()

# Set default value based on config or fallback to the first option
default_model = model_display_names[0]
if 'ModelSettings' in config and 'yolo_model' in config['ModelSettings']:
    selected_model = config['ModelSettings']['yolo_model']
    default_model = next((k for k, v in model_mapping.items() if v == selected_model), model_display_names[0])

model_var.set(default_model)

# Set up the dropdown menu
model_dropdown = ttk.Combobox(yolo_model_frame, textvariable=model_var, values=model_display_names, state="readonly")
model_dropdown.pack()

# Function to update the selected model in the config
def update_model_selection():
    selected_display_name = model_var.get()  # Get the display name
    if selected_display_name in model_mapping:  
        selected_model = model_mapping[selected_display_name]  # Map to the actual model file
        config['ModelSettings']['yolo_model'] = selected_model  # Save the actual model filename
    else:
        print(f"Error: {selected_display_name} is not a valid display name.")

# Bind the selection change to update the configuration
model_dropdown.bind("<<ComboboxSelected>>", lambda event: update_model_selection())




slider_label = tk.Label(root, text="Set Confidence Level:", bg=bg_color, fg=fg_color)  # Customize colors
slider_label.pack()
value_slider = tk.Scale(root, from_=0.0, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, bg=bg_color, fg=fg_color, troughcolor=switch_bg, activebackground=accent_color)  # Customize colors
value_slider.set(0.3)  # Set default value to 0.3
value_slider.pack()

# Get the window dimensions
window_width = 500
window_height = 600

# Calculate button positions
button_y = window_height - 100  # 100 pixels from the bottom
save_button_x = window_width * 0.25  # 25% from the left
start_button_x = window_width * 0.75  # 75% from the left

# Positioning buttons using place() with calculated positions
save_button = tk.Button(root, text="Save Configurations", command=save_config, bg="#0c039b", fg="white")
save_button.place(relx=0.25, rely=0.90, anchor="center")

# Use a brighter blue for the Run button to make it pop
run_button_color = "#2196f3"  # A bright, vibrant blue
start_button = tk.Button(root, text="Run Blurring Script", command=start_other_script, bg=run_button_color, fg="white")
start_button.place(relx=0.75, rely=0.90, anchor="center")

# Ensure all frames are aligned at the same level
options_frame.grid_rowconfigure(0, weight=1)  # Ensure all options are in the same row

def browse_file():
    file_path = filedialog.askopenfilename()  # Open file dialog to select a file
    input_path_entry.delete(0, tk.END)  # Clear the current entry
    input_path_entry.insert(0, file_path)  # Insert the selected file path

root.mainloop()
