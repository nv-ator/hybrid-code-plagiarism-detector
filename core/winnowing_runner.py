import subprocess
import os

def run_winnowing(input_folder, output_folder):
    command = [
        "copydetect",
        "--dir", input_folder,
        "--out", output_folder,
        "--format", "json"
    ]
    subprocess.run(command, capture_output=True)
