from fastapi import FastAPI, HTTPException
import logging
import subprocess
import os
import sys

app = FastAPI()

XC_API_DIR = os.path.join(os.path.dirname(__file__), "..")

# Replace this with the actual path to your Python interpreter
PYTHON_INTERPRETER_PATH = r"F:\A\xitecoin\venv\Scripts\python.exe"

def safe_print(text):
    try:
        # Try printing normally
        print(text)
    except UnicodeEncodeError:
        # If printing fails due to encoding issues, encode to 'utf-8' and decode to 'cp1252'
        encoded_text = text.encode('utf-8', errors='replace').decode('cp1252', errors='replace')
        # Print the encoded text
        sys.stdout.buffer.write(encoded_text.encode(sys.stdout.encoding, errors='replace'))
        # Print a warning
        print("\nWarning: Some characters could not be properly encoded and were replaced.")

@app.post("/start")
def start_xiteserver():
    try:
        # Command to execute
        command = [PYTHON_INTERPRETER_PATH, '-m', 'xite_network.xiteserver']
        
        # Run xiteserver subprocess
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=XC_API_DIR
        )
        
        # Log subprocess output
        safe_print("Subprocess stdout: " + result.stdout.strip())
        safe_print("Subprocess stderr: " + result.stderr.strip())

        # Check subprocess result
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Xitecoin server failed with output: {result.stderr.strip()}")

        return {"output": result.stdout}
    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def run_xiteclient(username: str, password: str):
    try:
        # Install requirements
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'], cwd=XC_API_DIR, check=True, capture_output=True)
        
        # Command to execute
        command = [PYTHON_INTERPRETER_PATH, '-m', 'xite_network.xiteclient', username, password, 'True']
        
        # Run xiteclient subprocess
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=XC_API_DIR
        )
        
        # Log subprocess output
        safe_print("Subprocess stdout: " + result.stdout.strip())
        safe_print("Subprocess stderr: " + result.stderr.strip())

        # Check subprocess result
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Xitecoin client failed with output: {result.stdout.strip()}")

        return {"output": result.stdout}
    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login/{username}/{password}")
def start_xiteclient(username: str, password: str):
    return run_xiteclient(username, password)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
