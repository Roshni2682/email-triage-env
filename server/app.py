@'
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Email triage environment is running"}
'@ | Set-Content .\server\app.py