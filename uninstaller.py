import subprocess
import sys

def install_package(package, index_url=None):
    cmd = [sys.executable, "-m", "pip", "uninstall"]
    if index_url:
        cmd.extend(["--index-url", index_url])
    cmd.append(package)
    subprocess.check_call(cmd)

# List of packages to install
packages = [
    "opencv-python",
    "ultralytics",
    "numpy",
    "configparser",
    "ffmpeg-python",
    # Ultralytics dependencies
    "matplotlib",
    "pandas",
    "pillow",
    "psutil",
    "py-cpuinfo",
    "pyyaml",
    "requests",
    "scipy",
    "seaborn",
    "tqdm",
    "ultralytics-thop",
    "omegaconf"
]

# Special cases with custom index URL
special_packages = [
    ("torch==2.2.2", "https://download.pytorch.org/whl/cpu"),
    ("torchvision==0.17.2", "https://download.pytorch.org/whl/cpu"),
    ("torchaudio==2.2.2", "https://download.pytorch.org/whl/cpu")
]

if __name__ == "__main__":
    for package in packages:
        try:
            install_package(package)
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")

    for package, index_url in special_packages:
        try:
            install_package(package, index_url)
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")