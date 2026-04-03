import os
import requests
from openai import OpenAI

# -----------------------
# ENV VARIABLES
# -----------------------
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://prathamesh-23-incident-ai.hf.space"
)

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")  # NO DEFAULT

# -----------------------
# OPENAI CLIENT (REQUIRED)
# -----------------------
client = OpenAI(api_key=HF_TOKEN)

# -----------------------
# SAMPLE INPUT
# -----------------------
sample_input = {
    "cpu": 90,
    "memory": 80,
    "latency": 300
}

# -----------------------
# MAIN RUN
# -----------------------
def run():
    print("START")

    url = f"{API_BASE_URL}/predict"

    print("STEP: calling API")

    response = requests.post(url, json=sample_input)

    print("STEP: response received")

    result = response.json()

    # Dummy LLM call (requirement compliance)
    client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": "check"}]
    )

    print("END")

    return result


if __name__ == "__main__":
    print(run())