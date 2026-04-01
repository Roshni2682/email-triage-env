from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Email triage environment is running"}

@app.get("/info")
def info():
    return {
        "name": "Email Triage OpenEnv",
        "version": "1.0.0",
        "tasks": ["task1", "task2", "task3"],
        "endpoints": ["/reset", "/step", "/state", "/info"]
    }

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()