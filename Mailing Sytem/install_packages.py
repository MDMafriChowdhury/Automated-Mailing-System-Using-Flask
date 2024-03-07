import subprocess

# Path to the Python interpreter
python_path = "/usr/bin/python3"  # You may need to adjust this path based on your system configuration

# List of packages to install
packages = ["Flask", "pymysql", "smtplib"]

# Install each package using pip
for package in packages:
    try:
        subprocess.run([python_path, "-m", "pip", "install", package], check=True)
        print(f"Successfully installed {package}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package}: {e}")