import os
import requests

# 🔥 FIXED PORT (CRITICAL)
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:7860")


def run():
    total_reward = 0.0
    steps = 0

    # START
    print("[START] task=incident_ai", flush=True)

    try:
        res = requests.post(f"{API_BASE_URL}/reset")

        # 🔥 DEBUG (DO NOT REMOVE)
        print("DEBUG RESET STATUS:", res.status_code, flush=True)
        print("DEBUG RESET TEXT:", res.text, flush=True)

        data = res.json()
        obs = data.get("observation", {})

    except Exception as e:
        print("RESET ERROR:", str(e), flush=True)
        print("[END] task=incident_ai score=0 steps=0", flush=True)
        return

    # FORCE LOOP
    while steps < 10:
        steps += 1

        # SAFE ACCESS
        cpu = obs.get("cpu", 0)
        latency = obs.get("latency", 0)
        memory = obs.get("memory", 0)

        # POLICY
        if cpu > 70:
            action = "scale_up"
        elif latency > 100:
            action = "restart_service"
        elif memory > 70:
            action = "check_database"
        else:
            action = "do_nothing"

        try:
            res = requests.post(
                f"{API_BASE_URL}/step",
                json={"action": action}
            )

            data = res.json()

            obs = data.get("observation", {})
            reward = float(data.get("reward", 0))
            done = data.get("done", False)

            total_reward += reward

            # STEP
            print(f"[STEP] step={steps} reward={reward}", flush=True)

            if done:
                break

        except Exception as e:
            print("STEP ERROR:", str(e), flush=True)
            break

    # END
    print(
        f"[END] task=incident_ai score={total_reward} steps={steps}",
        flush=True
    )


if __name__ == "__main__":
    run()