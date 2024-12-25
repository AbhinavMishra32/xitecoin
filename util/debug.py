from termcolor import colored
import inspect
import os
import re
from datetime import datetime
import threading

ENV = os.environ.get("ENV", "prod")
LOG_FILE = "client.log"
print_lock = threading.Lock()

def strip_color(text):
    # Regular expression to remove ANSI escape codes for color formatting
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def debug_log(*args, env="prod", **kwargs):
    env = "dev"
    dev_save = True
    if env == "dev":
        caller = inspect.currentframe().f_back #type: ignore
        if caller is not None:
            filename = os.path.basename(caller.f_code.co_filename)
            func_name = caller.f_code.co_name
            line_num = caller.f_lineno
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            debug_info = f"[{timestamp}] {filename}::{func_name} (line {line_num}):"
            message = ' '.join(map(str, args))
            log_message = f"{debug_info} {message}"

            # Print to console safely
            safe_print(log_message)
            if dev_save:
                log_message = f"{debug_info} {strip_color(message)}\n"
                if not os.path.exists(LOG_FILE):
                    with open(LOG_FILE, "w") as f:
                        f.write(log_message)
                with open(LOG_FILE, "a") as f:
                    f.write(log_message)
    elif env == "prod":
        caller = inspect.currentframe().f_back #type:ignore
        if caller is not None:
            filename = os.path.basename(caller.f_code.co_filename)
            func_name = caller.f_code.co_name
            line_num = caller.f_lineno
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            debug_info = f"[{timestamp}] {filename}::{func_name} (line {line_num}):"           
            message = ' '.join(map(str, args))
            log_message = f"{debug_info} {strip_color(message)}\n"  # Strip color codes

            # Write to log file
            if not os.path.exists(LOG_FILE):
                with open(LOG_FILE, "w") as f:
                    f.write(log_message)
            with open(LOG_FILE, "a") as f:
                f.write(log_message)

def safe_print(message):
    """Print function wrapped with a lock for thread safety."""
    with print_lock:
        print(message)

if __name__ == "__main__":
    debug_log(colored("Hello!", 'green'), environment="dev")
