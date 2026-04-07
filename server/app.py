from api import app
import uvicorn
import subprocess


# 🔥 THIS IS THE FIX — runs when app starts in HF
@app.on_event("startup")
def run_inference():
    try:
        subprocess.Popen(["python", "inference.py"])
    except Exception as e:
        print(f"Error running inference: {e}", flush=True)


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()