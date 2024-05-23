from termcolor import colored
import inspect
import os
import re
from datetime import datetime
import threading

LOG_FILE = "debug_log.txt"  # Specify the name of the log file
print_lock = threading.Lock()  # Define a lock for safe printing

def strip_color(text):
    # Regular expression to remove ANSI escape codes for color formatting
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def debug_log(*args, env="prod", **kwargs):
    env = "dev"
    if env == "dev":
        caller = inspect.currentframe().f_back
        if caller is not None:
            filename = os.path.basename(caller.f_code.co_filename)
            func_name = caller.f_code.co_name
            line_num = caller.f_lineno
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            debug_info = f"[LOG] [{timestamp}] {filename}::{func_name} (line {line_num}):"
            message = ' '.join(map(str, args))
            log_message = f"{debug_info} {message}\n"

            # Print to console safely
            safe_print(colored(log_message, 'yellow'))
    else:
        caller = inspect.currentframe().f_back
        if caller is not None:
            filename = os.path.basename(caller.f_code.co_filename)
            func_name = caller.f_code.co_name
            line_num = caller.f_lineno
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            debug_info = f"[LOG] [{timestamp}] {filename}::{func_name} (line {line_num}):"           
            message = ' '.join(map(str, args))
            log_message = f"{debug_info} {strip_color(message)}\n"  # Strip color codes

            # Write to log file
            with open(LOG_FILE, "a") as f:
                f.write(log_message)

def safe_print(message):
    """Print function wrapped with a lock for thread safety."""
    with print_lock:
        print(message)

if __name__ == "__main__":
    debug_log(colored("Hello!", 'green'), environment="dev")
