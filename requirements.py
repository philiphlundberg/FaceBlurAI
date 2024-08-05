import subprocess
import sys

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# List of packages to install
packages = [
    "opencv-python",
    "ultralytics",
    "numpy",
    "configparser",
    "ffmpeg-python"
]

if __name__ == "__main__":
    for package in packages:
        try:
            install_package(package)
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")
