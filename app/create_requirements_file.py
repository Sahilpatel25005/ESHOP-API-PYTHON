import subprocess

# Get installed packages
installed_packages = subprocess.check_output(["pip", "freeze"]).decode("utf-8")

# Write to requirements.txt
with open("requirements.txt", "w") as f:
    f.write(installed_packages)

print("requirements.txt file created successfully!")
