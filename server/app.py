from api import app
import uvicorn
import subprocess


def main():
    #  START SERVER
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    #  RUN INFERENCE FIRST (CRITICAL)
    try:
        subprocess.Popen(["python", "inference.py"])
    except Exception as e:
        print(f"Inference failed to start: {e}", flush=True)

    #  THEN START SERVER
    main()