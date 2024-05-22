from pdb import run
from fastapi import FastAPI, HTTPException
import subprocess
import os,sys

print(sys.executable)

app = FastAPI()


XC_API_DIR = os.path.join(os.path.dirname(__file__), "..")

@app.get("/")
def read_root():
    return {"Hello": "World"}

# @app.get("/balance")
# def read_balance():
#     try:
#         result = subprocess.run(['python', ''])


@app.post("/start")
def run_xiteclient(username, password):
    try:
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'], cwd=XC_API_DIR)
        subprocess.run([r'F:\A\xitecoin\venv\Scripts\activate'], shell=True, cwd=XC_API_DIR)
        result = subprocess.run(
            ['python', '-m', 'xite_network.xiteclient', username, password, 'True'],
            capture_output=True,
            text=True,
            cwd=XC_API_DIR
        )
        print("Xitecoin client started successfully")
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)
        return {"output": result.stdout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def startup_event():
    username = input("Enter username: ")
    password = input("Enter password: ")
    run_xiteclient(username, password)

@app.on_event("startup")
async def startup():
    await startup_event()

if __name__ == "__main__":
    import uvicorn
    #get username and pass from ui and add api to feed it to the console
    #for now using console input
    username = input("Enter username: ")
    password = input("Enter password: ")
    run_xiteclient(username, password)
    uvicorn.run(app, host = "0.0.0.0", port = 8000)