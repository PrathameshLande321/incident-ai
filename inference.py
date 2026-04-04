import os
import requests

# -----------------------
# ENV VARIABLES
# -----------------------
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
)

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")  # optional


# -----------------------
# OPTIONAL OPENAI (SAFE)
# -----------------------
client = None
try:
    if HF_TOKEN:
        from openai import OpenAI
        client = OpenAI(api_key=HF_TOKEN)
except:
    client = None


# -----------------------
# MAIN RUN
# -----------------------
def run():
    print("START")

    # -----------------------
    # STEP 0: INIT INCIDENT
    # -----------------------
    try:
        init_res = requests.post(
            f"{API_BASE_URL}/set_incident",
            json={"level": "hard"}
        )

        if init_res.status_code != 200:
            raise Exception("Init failed")

        init_data = init_res.json()

        if "error" in init_data or "detail" in init_data:
            raise Exception(init_data)

        print(f"STEP 0: initialized -> {init_data}")

    except Exception as e:
        print(f"STEP 0: INIT FAILED -> {e}")
        print("END total_reward=0.00")
        return {"total_reward": 0.0, "steps": 0}

    done = False
    step = 0
    total_reward = 0.0

    # -----------------------
    # LOOP
    # -----------------------
    while not done and step < 10:
        step += 1

        try:
            res = requests.get(f"{API_BASE_URL}/live_monitor").json()
        except Exception as e:
            print(f"STEP {step}: API ERROR -> {e}")
            break

        if "error" in res:
            print(f"STEP {step}: ERROR -> {res['error']}")
            break

        action = res.get("action", "unknown")
        reward = float(res.get("reward", 0.0))
        reason = res.get("reason", "N/A")
        done = res.get("done", False)

        total_reward += reward

        print(
            f"STEP {step}: action={action}, reward={reward:.2f}, done={done}, reason={reason}"
        )

    # -----------------------
    # OPTIONAL LLM CALL (SAFE)
    # -----------------------
    if client:
        try:
            client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{
                    "role": "user",
                    "content": "Summarize system performance in one line."
                }],
                max_tokens=20
            )
            print("STEP LLM: success")
        except Exception:
            print("STEP LLM: skipped")
    else:
        print("STEP LLM: skipped")

    print(f"END total_reward={total_reward:.2f}")

    return {
        "total_reward": total_reward,
        "steps": step
    }


if __name__ == "__main__":
    print(run())