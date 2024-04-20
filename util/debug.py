from termcolor import colored
import inspect
import os

def debug_log(*args, **kwargs):
    caller = inspect.currentframe()
    if caller is not None:
        filename = os.path.basename(caller.f_code.co_filename)
        func_name = caller.f_code.co_name
        line_num = caller.f_lineno
        debug_info = f"[DEBUG] {filename}::{func_name} (line {line_num}):"
        message = ' '.join(map(str, args))
        print(colored(f"{debug_info} {message}", 'yellow'))
    else:
        print(colored("[DEBUG] (unknown):", 'yellow'), *args, **kwargs)