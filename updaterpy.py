import os
import re

def fix_pyqt_portal_server_startup(file_path="pyqt.py"):
    """
    Fixes the duplicate portal server startup and ensures idempotent server start
    in the pyqt.py file.
    Also moves `handle_get_ads` into `EnhancedDeveloperPortalServer` class
    to resolve attribute error.

    Args:
        file_path (str): The path to the pyqt.py file.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return False

    print(f"Attempting to fix portal server startup and `handle_get_ads` in '{file_path}'...")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # --- Step 1: Remove the duplicate start_portal_server() call in main ---
        # Look for the pattern where it's called twice, potentially inside a try/except
        duplicate_call_pattern = re.compile(
            r"(main_window\.start_portal_server\(\)\s*)\s*" # First call (potentially in try block)
            r"(except Exception as e:\s*print\(f\"Portal server auto-start failed: {e}\"\)\s*)*" # Optional except block
            r"(\s*main_window\.start_portal_server\(\)\s*)", # The duplicate call to remove
            re.DOTALL
        )

        original_content = content
        content = duplicate_call_pattern.sub(r"\1\2", content) # Keep first call and except block

        if content == original_content:
            print("No duplicate 'main_window.start_portal_server()' found. Skipping removal.")
        else:
            print("Removed duplicate 'main_window.start_portal_server()' call in main function.")

        # --- Step 2: Make start_portal_server() idempotent and correctly initialize Flask app ---
        # First, ensure threading is imported for this new logic
        if "import threading" not in content:
            content = re.sub(r"(import logging)", r"\1\nimport threading", content)
            print("Added 'import threading'.")
        
        # New body for start_portal_server
        new_start_portal_server_body = """
        # Ensure the server only starts once
        if self.portal_server_thread and self.portal_server_thread.is_alive():
            logger.info("Portal server is already running.")
            return

        logger.info("Starting PythonCoin Developer Portal server...")
        self.portal_app = Flask(__name__) # Initialize Flask app
        self.setup_portal_cors() # Setup CORS
        self.register_portal_routes() # Register routes with this instance

        def run_server():
            # Suppress default Flask startup messages
            import logging
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)
            try:
                self.portal_app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
            except Exception as e:
                logger.error(f"Flask server error: {e}")

        self.portal_server_thread = threading.Thread(target=run_server)
        self.portal_server_thread.daemon = True # Allows the main program to exit even if threads are running
        self.portal_server_thread.start()
        logger.info(f"Developer Portal started on http://0.0.0.0:{self.port}")
"""
        # Find the entire start_portal_server definition and replace its content
        class_method_pattern = re.compile(
            r"(class\s+EnhancedDeveloperPortalServer\(.*?:\s*.*?)(\s*def\s+start_portal_server\s*\(self\):.*?(?=\s*def\s|\s*@self\.portal_app\.route|\s*\Z))",
            re.DOTALL
        )

        def replace_start_portal_server(match):
            class_prefix = match.group(1)
            indent_match = re.search(r"(\s*)def\s+start_portal_server", match.group(2))
            method_indent = indent_match.group(1) if indent_match else "    "

            indented_new_body = "\n".join([
                method_indent + line for line in new_start_portal_server_body.strip().split('\n')
            ])

            return f"{class_prefix}{method_indent}def start_portal_server(self):\n{indented_new_body}\n"

        content, num_replacements = class_method_pattern.subn(replace_start_portal_server, content, count=1)
        
        if num_replacements > 0:
            print("Successfully updated 'start_portal_server' for idempotent startup.")
            
            # Ensure self.portal_app is initialized in __init__ and thread attribute exists
            init_pattern = re.compile(
                r"(def\s+__init__\(self,.*?):.*?)\n(\s*self\.db_manager\s*=)",
                re.DOTALL
            )
            if not re.search(r"self\.portal_app\s*=\s*Flask", content):
                content = re.sub(
                    r"(def\s+__init__\(self,.*?):\n)",
                    r"\1        self.portal_app = None # Initialize Flask app instance\n        self.portal_server_thread = None # Initialize thread attribute\n",
                    content,
                    flags=re.DOTALL
                )
                print("Ensured self.portal_app and self.portal_server_thread initialized in __init__.")
            else:
                 print("self.portal_app already initialized in __init__.")

            # Ensure setup_portal_cors() is called somewhere reachable from run()
            if "self.setup_portal_cors()" not in content:
                # Add it to init if not present elsewhere.
                # This might need manual adjustment if CORS setup is complex.
                content = re.sub(
                    r"(def\s+__init__\(self,.*?):.*?)(\s*self\.db_manager\s*=)",
                    r"\1        self.setup_portal_cors()\n\2",
                    content,
                    flags=re.DOTALL
                )
                print("Added 'self.setup_portal_cors()' to __init__ if missing.")

        else:
            print("Could not find 'start_portal_server' method to update. File might be significantly different.")
            return False

        # --- Step 3: Move handle_get_ads into EnhancedDeveloperPortalServer class ---
        # Find the handle_get_ads definition outside the class
        handle_get_ads_definition_pattern = re.compile(
            r"(\s*def\s+handle_get_ads\(self\):\s*.*?)(?=\s*def\s+|\s*class\s+|\s*\Z)",
            re.DOTALL
        )

        # Find the RobustPythonCoinHandler class which uses it
        robust_handler_class_pattern = re.compile(
            r"(class\s+RobustPythonCoinHandler\(BaseHTTPRequestHandler\):\s*.*?)(def\s+do_GET\(self\):.*?)(elif\s+path\s*==\s*'/ads':.*?response\s*=\s*self\.server_instance\.handle_get_ads\(\)\s*self\.wfile\.write\(response\.encode\(\)\)\s*)",
            re.DOTALL
        )

        # Extract the content of handle_get_ads, then remove it from its old location
        handle_get_ads_match = re.search(handle_get_ads_definition_pattern, content)
        if handle_get_ads_match:
            handle_get_ads_content = handle_get_ads_match.group(1).strip()
            # Remove the original handle_get_ads definition
            content = handle_get_ads_definition_pattern.sub("", content)
            print("Removed original 'handle_get_ads' definition from its old location.")

            # Find the EnhancedDeveloperPortalServer class
            enhanced_server_class_pattern = re.compile(
                r"(class\s+EnhancedDeveloperPortalServer\(QThread\):\s*.*?)(def\s+find_available_port\(self,.*?):)",
                re.DOTALL
            )
            
            # Insert handle_get_ads as a method within EnhancedDeveloperPortalServer
            def insert_handle_get_ads_method(match):
                class_prefix = match.group(1)
                method_indent = "    " # Standard class method indentation
                
                # Adjust indentation of the extracted handle_get_ads content
                indented_handle_get_ads = "\n".join([
                    method_indent + line for line in handle_get_ads_content.split('\n')
                ])
                
                # Insert it just before 'def find_available_port' for consistency
                return f"{class_prefix}\n{indented_handle_get_ads}\n\n{match.group(2)}"
            
            content, num_insertions = enhanced_server_class_pattern.subn(insert_handle_get_ads_method, content, count=1)
            if num_insertions > 0:
                print("Successfully moved 'handle_get_ads' into 'EnhancedDeveloperPortalServer' as a method.")
            else:
                print("Could not find insertion point for 'handle_get_ads' in 'EnhancedDeveloperPortalServer'. Manual intervention might be needed.")

            # Also ensure the RobustPythonCoinHandler's do_GET method correctly calls it
            # The current code already does `self.server_instance.handle_get_ads()`,
            # which will now correctly resolve since it's a method of the instance.
            
            # Add setup_portal_cors() if it's not present. This helper is crucial.
            if "def setup_portal_cors(self):" not in content:
                # Find the EnhancedDeveloperPortalServer class definition again
                class_start = re.search(r"(class\s+EnhancedDeveloperPortalServer\(QThread\):)", content)
                if class_start:
                    class_indent = re.match(r"(\s*)class", class_start.group(0)).group(1)
                    cors_method = f"""
{class_indent}    def setup_portal_cors(self):
{class_indent}        \"\"\"Setup Flask CORS for the portal app.\"\"\"
{class_indent}        from flask_cors import CORS
{class_indent}        CORS(self.portal_app)
"""
                    # Insert it after __init__ or another logical place
                    init_method_end = re.search(r"(def\s+__init__\(self,.*?\):\s*.*?)(def\s+find_available_port)", content, re.DOTALL)
                    if init_method_end:
                        content = content[:init_method_end.start(2)] + cors_method + content[init_method_end.start(2):]
                        print("Added 'setup_portal_cors' method to EnhancedDeveloperPortalServer.")
                    else:
                        print("Could not find suitable place to add 'setup_portal_cors'. Manual addition may be required.")
            else:
                print("'setup_portal_cors' method already exists.")

            # Ensure Flask is imported
            if "from flask import Flask, jsonify, request" not in content:
                content = re.sub(
                    r"(from flask import Flask, jsonify)",
                    r"\1, request",
                    content,
                    flags=re.DOTALL
                )
                print("Ensured 'request' is imported for Flask operations.")
                
        else:
            print("Could not find 'handle_get_ads' definition to move. File might already be updated or structured differently.")


        # Write the modified content back to a new file
        updated_file_path = file_path + ".new"
        with open(updated_file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Replace the original file with the updated one
        os.replace(updated_file_path, file_path)
        print(f"\nSuccessfully fixed '{file_path}'.")
        print("Please verify the changes and restart your PyQt application.")
        return True

    except Exception as e:
        print(f"An error occurred during file modification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting PyQt.py endpoint fixer script...")
    
    confirmation = input("This script will modify your 'pyqt.py' file to fix server startup and ad handler logic. Please ensure you have a backup. Type 'yes' to proceed: ").lower()
    
    if confirmation == 'yes':
        if fix_pyqt_portal_server_startup("pyqt.py"):
            print("Fix applied. Restart your PythonCoin PyQt client.")
        else:
            print("Fix failed or was not necessary.")
    else:
        print("Update cancelled by user.")