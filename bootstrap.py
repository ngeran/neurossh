import os
import sys
import subprocess
import venv
import shutil
from pathlib import Path

def print_status(message: str):
    print(f"\033[1;32m[NeuroSSH-System]\033[0m {message}")

def print_error(message: str):
    print(f"\033[1;31m[!] Error:\033[0m {message}")

def setup_and_launch():
    app_dir = Path(__file__).parent
    venv_dir = app_dir / ".venv"
    main_script = app_dir / "main.py"
    # Added all specific dependencies for the final build
    requirements = ["textual", "paramiko", "pyte", "cryptography", "PyYAML"]

    if not main_script.exists():
        print_error("main.py not found in the current directory.")
        sys.exit(1)

    if not venv_dir.exists():
        print_status("Initializing new neural environment (.venv)...")
        venv.create(venv_dir, with_pip=True)
    else:
        print_status("Neural environment detected. Resuming...")

    if sys.platform == "win32":
        python_exe = venv_dir / "Scripts" / "python.exe"
        pip_exe = venv_dir / "Scripts" / "pip.exe"
    else:
        python_exe = venv_dir / "bin" / "python"
        pip_exe = venv_dir / "bin" / "pip"

    print_status(f"Syncing dependencies: {', '.join(requirements)}...")
    try:
        subprocess.check_call([str(pip_exe), "install", "--upgrade", "pip"], 
                              stdout=subprocess.DEVNULL)
        subprocess.check_call([str(pip_exe), "install", *requirements], 
                              stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        sys.exit(1)

    print_status("Launching NeuroSSH Interface...")
    try:
        subprocess.run([str(python_exe), str(main_script)])
    except KeyboardInterrupt:
        print_status("Connection Terminated by User.")
    except Exception as e:
        print_error(f"Execution failed: {e}")

if __name__ == "__main__":
    setup_and_launch()
