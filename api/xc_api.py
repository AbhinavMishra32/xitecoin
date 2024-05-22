from fastapi import FastAPI, HTTPException
import logging
import subprocess
import os

app = FastAPI()

XC_API_DIR = os.path.join(os.path.dirname(__file__), "..")

def run_xiteclient(username: str, password: str):
    try:
        # Install requirements
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'], cwd=XC_API_DIR, check=True, capture_output=True)
        
        # Get Python interpreter
        python_interpreter = subprocess.run(['which', 'python'], capture_output=True, text=True).stdout.strip()
        
        # Command to execute
        command = [python_interpreter, '-m', 'xite_network.xiteclient', username, password, 'True']
        
        logging.debug(f"Executing command: {' '.join(command)}")
        
        # Run xiteclient subprocess
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=XC_API_DIR
        )
        
        # Log subprocess output
        logging.debug(f"Subprocess stdout: {result.stdout.strip()}")
        logging.debug(f"Subprocess stderr: {result.stderr.strip()}")

        # Check subprocess result
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Xitecoin client failed with output: {result.stdout.strip()}")

        return {"output": result.stdout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/start/{username}/{password}")
def start_xiteclient(username: str, password: str):
    return run_xiteclient(username, password)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
