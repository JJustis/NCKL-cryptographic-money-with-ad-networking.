import sys
import subprocess
import os
import shutil
import platform
import requests
import zipfile
import io
import time
import getpass # For secure password input
import re

# --- Configuration ---
PYTHON_MAJOR_VERSION = "3.12" # Target Python major.minor version
PYTHON_VERSION = "3.12.0" # Target Python full version (for installer URL)
PYTHON_INSTALLER_URL = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe" 

XAMPP_INSTALLER_URL = "https://sourceforge.net/projects/xampp/files/XAMPP%20Windows/8.2.4/xampp-windows-x64-8.2.4-0-VS16-installer.exe/download"
XAMPP_INSTALL_DIR = "C:\\xampp" # Default XAMPP installation directory

ZIP_FILE_NAME = "livepy.zip" # Name of the application ZIP file
APP_SUB_DIR_IN_ZIP = "livepy/pythoncoin" # Path inside the zip file to the application root

OLD_DB_PASSWORD = "" # The password string to replace in files
# --- End Configuration ---

APP_INSTALLER_ROOT_DIR = os.path.abspath(os.path.dirname(__file__)) # Directory where install.exe runs and extracts its files

def log(message, level="INFO"):
    print(f"[{level}] [INSTALLER] {message}")

def is_admin():
    """Check if the script is running with administrator privileges on Windows."""
    try:
        # This will raise AttributeError on Windows, which is expected
        return os.getuid() == 0 
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def check_python_installed(version_prefix):
    """Checks if a specific Python version is available via 'py' launcher."""
    try:
        result = subprocess.run(['py', f'-{version_prefix}', '-c', 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'], 
                                capture_output=True, text=True, check=True)
        detected_version = result.stdout.strip()
        if detected_version == version_prefix:
            log(f"Python {version_prefix} detected using 'py' launcher.")
            return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass # py launcher might not be in PATH or version not found
    log(f"Python {version_prefix} not found using 'py' launcher.")
    return False

def download_file(url, target_path):
    """Downloads a file from a URL."""
    log(f"Downloading from {url} to {target_path}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(target_path, 'wb') as f:
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded_size += len(chunk)
                if total_size > 0:
                    progress = (downloaded_size / total_size) * 100
                    sys.stdout.write(f"\r[INFO] [INSTALLER] Download progress: {progress:.2f}%")
                    sys.stdout.flush()
            sys.stdout.write("\n") # Newline after progress bar
        log("Download complete.")
        return True
    except requests.exceptions.RequestException as e:
        log(f"Error downloading: {e}", level="ERROR")
        return False

def install_python_windows(installer_path):
    """Installs Python silently on Windows."""
    log(f"Installing Python from {installer_path}...")
    
    if not is_admin():
        log("WARNING: Python installation usually requires Administrator privileges.")
        log("Please run this installer as Administrator if the Python installation fails.", level="WARNING")
        time.sleep(5)

    # Standard silent install for all users, adds to PATH
    command = [installer_path, "/quiet", "InstallAllUsers=1", "PrependPath=1"]
    
    try:
        log(f"Executing: {' '.join(command)}")
        # Use shell=True for windows installers for better path resolution if needed
        process = subprocess.run(command, check=True, capture_output=True, text=True, shell=True, timeout=300) # 5 min timeout
        log(f"Python installation stdout:\n{process.stdout}")
        log(f"Python installation stderr:\n{process.stderr}")
        log("Python installation initiated successfully.")
        log("The installer might run in the background. Please wait for it to complete.")
        time.sleep(15) # Give system a moment to update PATH if necessary
        return True
    except subprocess.CalledProcessError as e:
        log(f"Python installation failed with exit code {e.returncode}: {e}", level="ERROR")
        log(f"Stdout: {e.stdout}", level="ERROR")
        log(f"Stderr: {e.stderr}", level="ERROR")
        return False
    except FileNotFoundError:
        log(f"Python installer not found at {installer_path}", level="ERROR")
        return False
    except subprocess.TimeoutExpired:
        log(f"Python installation timed out after 5 minutes. It may still be running in the background.", level="WARNING")
        return True # Assume it's still running, might succeed later

def get_python_executable(version_prefix):
    """Attempts to get the full path to the python executable for a given version."""
    try:
        result = subprocess.run(['py', f'-{version_prefix}', '-c', 'import sys; print(sys.executable)'], 
                                capture_output=True, text=True, check=True)
        python_exe = result.stdout.strip()
        if os.path.exists(python_exe):
            return python_exe
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    if platform.system() == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            path_candidate = os.path.join(local_app_data, "Programs", "Python", f"Python{version_prefix.replace('.', '')}", "python.exe")
            if os.path.exists(path_candidate):
                return path_candidate
        
        program_files = os.environ.get("PROGRAMFILES")
        if program_files:
            path_candidate = os.path.join(program_files, "Python", f"Python{version_prefix.replace('.', '')}", "python.exe")
            if os.path.exists(path_candidate):
                return path_candidate
        
        program_files_x86 = os.environ.get("PROGRAMFILES(X86)")
        if program_files_x86:
            path_candidate = os.path.join(program_files_x86, "Python", f"Python{version_prefix.replace('.', '')}", "python.exe")
            if os.path.exists(path_candidate):
                return path_candidate

    log(f"Could not automatically locate Python {version_prefix} executable.")
    return None

def install_dependencies(python_executable, requirements_file):
    """Installs Python dependencies."""
    log(f"Installing dependencies using {python_executable} from {requirements_file}...")
    try:
        command = [python_executable, '-m', 'pip', 'install', '--upgrade', 'r', 'pip', 'setuptools'] 
        log(f"Executing: {' '.join(command)}")
        subprocess.run(command, check=True, capture_output=True, text=True) 

        command = [python_executable, '-m', 'pip', 'install', '-r', requirements_file]
        log(f"Executing: {' '.join(command)}")
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        log(f"Dependencies installation stdout:\n{process.stdout}")
        log(f"Dependencies installation stderr:\n{process.stderr}")
        log("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Dependencies installation failed: {e}", level="ERROR")
        log(f"Stdout: {e.stdout}", level="ERROR")
        log(f"Stderr: {e.stderr}", level="ERROR")
        return False
    except FileNotFoundError:
        log(f"Python executable not found at {python_executable}", level="ERROR")
        return False

def install_xampp(installer_path):
    """Installs XAMPP silently on Windows."""
    log(f"Installing XAMPP from {installer_path} to {XAMPP_INSTALL_DIR}...")

    if os.path.exists(XAMPP_INSTALL_DIR):
        log(f"XAMPP already detected at {XAMPP_INSTALL_DIR}. Skipping installation.", level="WARNING")
        return True
        
    if not is_admin():
        log("WARNING: XAMPP installation requires Administrator privileges.", level="WARNING")
        log("Please run this installer as Administrator if XAMPP installation fails.", level="WARNING")
        time.sleep(5)

    # /S is the silent installation flag for NSIS installers (used by XAMPP)
    # /D=C:\xampp sets the installation directory
    command = [installer_path, "/S", f"/D={XAMPP_INSTALL_DIR}"]
    
    try:
        log(f"Executing: {' '.join(command)}")
        process = subprocess.run(command, check=True, capture_output=True, text=True, shell=True, timeout=600) # 10 min timeout
        log(f"XAMPP installation stdout:\n{process.stdout}")
        log(f"XAMPP installation stderr:\n{process.stderr}")
        log("XAMPP installation initiated successfully.")
        log("Please wait, XAMPP installation can take several minutes to complete.")
        log("Checking for XAMPP files...")
        # Wait until some XAMPP files are present
        start_time = time.time()
        while not os.path.exists(os.path.join(XAMPP_INSTALL_DIR, "xampp-control.exe")):
            if time.time() - start_time > 300: # 5 minutes wait
                log("Timed out waiting for XAMPP files to appear. Installation may have failed or is taking very long.", level="ERROR")
                return False
            time.sleep(5)
        log("XAMPP files detected. Installation likely complete.")
        return True
    except subprocess.CalledProcessError as e:
        log(f"XAMPP installation failed with exit code {e.returncode}: {e}", level="ERROR")
        log(f"Stdout: {e.stdout}", level="ERROR")
        log(f"Stderr: {e.stderr}", level="ERROR")
        return False
    except FileNotFoundError:
        log(f"XAMPP installer not found at {installer_path}", level="ERROR")
        return False
    except subprocess.TimeoutExpired:
        log(f"XAMPP installation timed out after 10 minutes. It may still be running in the background.", level="WARNING")
        return True


def set_mysql_root_password(new_password):
    """Sets the MySQL root password after XAMPP installation."""
    log("Attempting to set MySQL root password...")
    mysql_bin_dir = os.path.join(XAMPP_INSTALL_DIR, "mysql", "bin")
    mysql_exe = os.path.join(mysql_bin_dir, "mysql.exe")
    mysqladmin_exe = os.path.join(mysql_bin_dir, "mysqladmin.exe")

    if not os.path.exists(mysql_exe):
        log(f"MySQL executable not found at {mysql_exe}. XAMPP MySQL might not be installed correctly.", level="ERROR")
        return False

    # Start MySQL if not running
    log("Starting MySQL service...")
    try:
        subprocess.run(["net", "start", "mysql"], check=False, capture_output=True, text=True)
        time.sleep(5) # Give it time to start
    except Exception as e:
        log(f"Error starting MySQL service: {e}", level="WARNING")

    # Change password
    # Initially, root has no password.
    # On some XAMPP versions, root might have a default password like 'root'. We'll try blank first.
    command_set_pass = [mysqladmin_exe, "-u", "root", "password", new_password]
    command_flush_priv = [mysql_exe, "-u", "root", "-p" + new_password, "-e", "FLUSH PRIVILEGES;"]

    max_retries = 5
    for attempt in range(max_retries):
        try:
            log(f"Attempt {attempt + 1}: Setting root password with mysqladmin...")
            result_set_pass = subprocess.run(command_set_pass, check=True, capture_output=True, text=True, timeout=60)
            log(f"mysqladmin stdout:\n{result_set_pass.stdout}")
            log(f"mysqladmin stderr:\n{result_set_pass.stderr}")
            
            log(f"Attempt {attempt + 1}: Flushing privileges...")
            result_flush_priv = subprocess.run(command_flush_priv, check=True, capture_output=True, text=True, timeout=60)
            log(f"mysql flush stdout:\n{result_flush_priv.stdout}")
            log(f"mysql flush stderr:\n{result_flush_priv.stderr}")

            log("MySQL root password set successfully.")
            return True
        except subprocess.CalledProcessError as e:
            log(f"MySQL password setting failed (attempt {attempt + 1}): {e}", level="ERROR")
            log(f"Stdout: {e.stdout}", level="ERROR")
            log(f"Stderr: {e.stderr}", level="ERROR")
            time.sleep(5)
        except subprocess.TimeoutExpired:
            log(f"MySQL password setting timed out (attempt {attempt + 1}).", level="ERROR")
            time.sleep(5)
        except Exception as e:
            log(f"An unexpected error occurred during MySQL password setting: {e}", level="ERROR")
            time.sleep(5)
    
    log("Failed to set MySQL root password after multiple attempts.", level="ERROR")
    return False

def update_application_passwords(app_install_dir, new_password):
    """Updates hardcoded password in application files."""
    log(f"Updating application files with new password in {app_install_dir}...")
    
    files_to_update = [
        os.path.join(app_install_dir, "pyqt.py"),
        os.path.join(app_install_dir, "pythoncoin.py"),
        os.path.join(app_install_dir, "config.php"),
        # Add any other files that contain the old password
    ]

    updated_count = 0
    for filepath in files_to_update:
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Use re.sub for robust replacement, in case OLD_DB_PASSWORD appears multiple times
                new_content = re.sub(re.escape(OLD_DB_PASSWORD), re.escape(new_password), content)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    log(f"Updated password in: {filepath}")
                    updated_count += 1
                else:
                    log(f"Old password not found in: {filepath} (or no change needed)")
            except Exception as e:
                log(f"Error updating password in {filepath}: {e}", level="ERROR")
        else:
            log(f"File not found: {filepath} (Skipping password update)", level="WARNING")
    
    log(f"Finished updating passwords in {updated_count} files.")
    return True

def create_run_scripts(app_install_dir, python_version_prefix):
    """Creates run_app.bat and run_app.sh scripts."""
    log("Creating run_app.bat and run_app.sh...")
    app_script_path = os.path.join(app_install_dir, 'pyqt.py')

    # For Windows (run_app.bat)
    bat_content = f"""@echo off
REM This script runs the PythonCoin application
REM using the Python {python_version_prefix} environment.

py -{python_version_prefix} "{app_script_path}"
pause
"""
    bat_path = os.path.join(app_install_dir, "run_app.bat")
    try:
        with open(bat_path, "w") as f:
            f.write(bat_content)
        log(f"Created {bat_path}")
    except IOError as e:
        log(f"Error creating run_app.bat: {e}", level="ERROR")
        return False

    # For Linux/macOS (run_app.sh)
    sh_content = f"""#!/bin/bash
# This script runs the PythonCoin application
# using the Python {python_version_prefix} environment.

# Ensure 'py' launcher is available or use direct python executable if known
if command -v py &> /dev/null
then
    py -{python_version_prefix} "{app_script_path}"
else
    if command -v python{python_version_prefix} &> /dev/null
    then
        python{python_version_prefix} "{app_script_path}"
    else
        echo "Neither 'py' launcher nor 'python{python_version_prefix}' found."
        echo "Please ensure Python {python_version_prefix} is installed and in your PATH."
        read -p "Press Enter to continue..."
    fi
fi
"""
    sh_path = os.path.join(app_install_dir, "run_app.sh")
    try:
        with open(sh_path, "w") as f:
            f.write(sh_content)
        os.chmod(sh_path, 0o755) # Make it executable
        log(f"Created {sh_path}")
    except IOError as e:
        log(f"Error creating run_app.sh: {e}", level="ERROR")
        return False
    except OSError as e: # For chmod
        log(f"Error making run_app.sh executable: {e}", level="ERROR")
        return False

    return True

def main():
    log("Starting PythonCoin Automated Installer...")
    log(f"Installer root directory: {APP_INSTALLER_ROOT_DIR}")

    if not is_admin():
        log("RECOMMENDATION: Please run this installer as Administrator for full functionality (Python and XAMPP installation).", level="WARNING")
        log("Some steps might fail without elevated privileges.", level="WARNING")
        input("Press Enter to continue, or close and restart as Administrator...")

    # --- Step 0: Prompt for application installation path ---
    default_app_install_dir = os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "PythonCoin")
    app_install_dir_input = input(f"Enter desired application installation directory (default: {default_app_install_dir}): ")
    app_install_dir = os.path.abspath(app_install_dir_input if app_install_dir_input else default_app_install_dir)
    
    if not os.path.exists(app_install_dir):
        try:
            os.makedirs(app_install_dir)
            log(f"Created application directory: {app_install_dir}")
        except OSError as e:
            log(f"Error creating application directory {app_install_dir}: {e}", level="ERROR")
            log("Please choose a different directory or ensure you have permissions.", level="ERROR")
            sys.exit(1)
    
    log(f"Application will be installed to: {app_install_dir}")

    # --- Step 1: Python Installation ---
    log(f"Checking for Python {PYTHON_MAJOR_VERSION}...")
    if platform.system() == "Windows":
        if not check_python_installed(PYTHON_MAJOR_VERSION):
            log(f"Python {PYTHON_MAJOR_VERSION} not found. Attempting to install...")
            installer_filename = os.path.basename(PYTHON_INSTALLER_URL)
            temp_installer_path = os.path.join(APP_INSTALLER_ROOT_DIR, installer_filename)
            
            if not download_file(PYTHON_INSTALLER_URL, temp_installer_path):
                log("Failed to download Python installer. Please check internet connection or download manually.", level="ERROR")
                sys.exit(1)
            
            if not install_python_windows(temp_installer_path):
                log("Failed to install Python. Please check the logs above.", level="ERROR")
                sys.exit(1)
            
            # Clean up installer
            if os.path.exists(temp_installer_path):
                try:
                    os.remove(temp_installer_path)
                    log(f"Cleaned up {installer_filename}.")
                except OSError as e:
                    log(f"Warning: Could not remove temporary installer file {temp_installer_path}: {e}", level="WARNING")
            
            # Re-check if Python is now installed and accessible
            if not check_python_installed(PYTHON_MAJOR_VERSION):
                log(f"Python {PYTHON_MAJOR_VERSION} installation completed but is not accessible via 'py' launcher.", level="ERROR")
                log("Please ensure Python was installed correctly and system PATH is updated (a reboot might be required).", level="ERROR")
                sys.exit(1)
        else:
            log(f"Python {PYTHON_MAJOR_VERSION} is already installed.")
    else: # For Linux/macOS, we'll assume Python 3.12 is manually managed or already present
        log("Python installation for non-Windows systems is not automated.", level="WARNING")
        log(f"Please ensure Python {PYTHON_MAJOR_VERSION} is installed and accessible via 'py -{PYTHON_MAJOR_VERSION}' or 'python{PYTHON_MAJOR_VERSION}'.", level="WARNING")
        try:
            subprocess.run(['py', f'-{PYTHON_MAJOR_VERSION}', '-c', ''], check=True, capture_output=True)
            log(f"Using 'py -{PYTHON_MAJOR_VERSION}' for dependency installation.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run([f'python{PYTHON_MAJOR_VERSION}', '-c', ''], check=True, capture_output=True)
                log(f"Using 'python{PYTHON_MAJOR_VERSION}' for dependency installation.")
            except (subprocess.CalledProcessError, FileNotFoundError):
                log(f"Python {PYTHON_MAJOR_VERSION} not found. Please install manually.", level="ERROR")
                sys.exit(1)
            
    python_exe_path = get_python_executable(PYTHON_MAJOR_VERSION)
    if not python_exe_path:
        log(f"Failed to find executable for Python {PYTHON_MAJOR_VERSION}.", level="ERROR")
        log("Ensure Python is installed correctly and in system PATH.", level="ERROR")
        sys.exit(1)

    # --- Step 2: XAMPP Installation ---
    log("Starting XAMPP installation process...")
    xampp_installer_filename = os.path.basename(XAMPP_INSTALLER_URL).split("?")[0] # Clean up URL to get filename
    temp_xampp_installer_path = os.path.join(APP_INSTALLER_ROOT_DIR, xampp_installer_filename)

    if not os.path.exists(os.path.join(XAMPP_INSTALL_DIR, "xampp-control.exe")): # Check if XAMPP already installed
        if not download_file(XAMPP_INSTALLER_URL, temp_xampp_installer_path):
            log("Failed to download XAMPP installer. Please check internet connection or download manually.", level="ERROR")
            sys.exit(1)
        
        if not install_xampp(temp_xampp_installer_path):
            log("Failed to install XAMPP. Please check the logs above.", level="ERROR")
            sys.exit(1)
        
        # Clean up installer
        if os.path.exists(temp_xampp_installer_path):
            try:
                os.remove(temp_xampp_installer_path)
                log(f"Cleaned up {xampp_installer_filename}.")
            except OSError as e:
                log(f"Warning: Could not remove temporary XAMPP installer file {temp_xampp_installer_path}: {e}", level="WARNING")
    else:
        log("XAMPP is already installed. Skipping XAMPP installation.", level="INFO")

    # --- Step 3: Prompt for MySQL Root Password ---
    log("\nNow configuring MySQL root password for XAMPP.")
    new_mysql_password = getpass.getpass("Enter your desired MySQL root password: ")
    confirm_mysql_password = getpass.getpass("Confirm your desired MySQL root password: ")

    if new_mysql_password != confirm_mysql_password:
        log("Passwords do not match. Please restart the installer and try again.", level="ERROR")
        sys.exit(1)
    if not new_mysql_password:
        log("Password cannot be empty. Please restart the installer and provide a password.", level="ERROR")
        sys.exit(1)
    
    log("Attempting to set MySQL root password. This may take a moment...", level="INFO")
    if not set_mysql_root_password(new_mysql_password):
        log("Failed to set MySQL root password. Please configure it manually in XAMPP/phpMyAdmin.", level="ERROR")
        log("The application files will still be updated with your chosen password.", level="WARNING")
        # Do not exit, continue to update app files

    # --- Step 4: Extract Application Files ---
    log(f"Extracting {ZIP_FILE_NAME} to {app_install_dir}...")
    temp_zip_path = os.path.join(APP_INSTALLER_ROOT_DIR, ZIP_FILE_NAME)
    
    if not os.path.exists(temp_zip_path):
        log(f"Error: Application ZIP file '{ZIP_FILE_NAME}' not found. Please place it next to this installer.", level="ERROR")
        sys.exit(1)

    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            # Create the final destination path for livepy/pythoncoin within app_install_dir
            final_app_target_path = os.path.join(app_install_dir, *APP_SUB_DIR_IN_ZIP.split('/'))
            os.makedirs(final_app_target_path, exist_ok=True) # Ensure target dir exists
            
            # Extract content of livepy/pythoncoin into the app_install_dir
            for member in zip_ref.namelist():
                # Check if member is inside the desired subdirectory
                if member.startswith(APP_SUB_DIR_IN_ZIP + '/'):
                    # Remove the livepy/pythoncoin/ prefix and join with app_install_dir
                    target_path = os.path.join(app_install_dir, member[len(APP_SUB_DIR_IN_ZIP)+1:])
                    if not os.path.isdir(target_path): # Only extract files, directories are created by parents
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        with open(target_path, "wb") as outfile, zip_ref.open(member) as infile:
                            shutil.copyfileobj(infile, outfile)
            log(f"Application files extracted to: {app_install_dir}")
    except zipfile.BadZipFile:
        log(f"Error: '{ZIP_FILE_NAME}' is a bad ZIP file.", level="ERROR")
        sys.exit(1)
    except Exception as e:
        log(f"Error extracting application files: {e}", level="ERROR")
        sys.exit(1)

    # --- Step 5: Install Python Dependencies ---
    requirements_file = os.path.join(app_install_dir, APP_SUB_DIR_IN_ZIP, "requirements.txt")
    if not os.path.exists(requirements_file):
        # Fallback for old location
        requirements_file = os.path.join(APP_INSTALLER_ROOT_DIR, "requirements.txt") 
        if not os.path.exists(requirements_file):
            log(f"Error: requirements.txt not found in extracted app directory or installer directory.", level="ERROR")
            sys.exit(1)
        else:
            log(f"Using requirements.txt from installer directory: {requirements_file}")

    if not install_dependencies(python_exe_path, requirements_file):
        log("Failed to install Python dependencies.", level="ERROR")
        sys.exit(1)

    # --- Step 6: Update Application Files with New Password ---
    final_app_source_dir = os.path.join(app_install_dir, *APP_SUB_DIR_IN_ZIP.split('/'))
    if not update_application_passwords(final_app_source_dir, new_mysql_password):
        log("Password update in application files encountered errors.", level="WARNING")

    # --- Step 7: Create Run Scripts ---
    if not create_run_scripts(final_app_source_dir, PYTHON_MAJOR_VERSION):
        log("Failed to create run scripts.", level="ERROR")
        sys.exit(1)

    log("\n--- Installation Complete! ---")
    log(f"PythonCoin application installed to: {final_app_source_dir}")
    log(f"You can start the application using 'run_app.bat' (Windows) or './run_app.sh' (Linux/macOS) in that directory.")
    log(f"XAMPP installed to: {XAMPP_INSTALL_DIR}")
    log("Remember to start Apache and MySQL services via XAMPP Control Panel if they are not running.")
    log(f"For PHP files to be served by Apache, you may need to copy your {APP_SUB_DIR_IN_ZIP} folder to {XAMPP_INSTALL_DIR}\\htdocs.")
    input("Press Enter to exit the installer.")

if __name__ == "__main__":
    main()