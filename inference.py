import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def run():
    total_reward = 0.0
    steps = 0

    #  START BLOCK (STRICT FORMAT)
    print("[START] task=incident_ai", flush=True)

    try:
        res = requests.post(f"{API_BASE_URL}/reset")
        data = res.json()

        obs = data["observation"]
        done = data["done"]

    except:
        print("[END] task=incident_ai score=0 steps=0", flush=True)
        return

    while not done and steps < 10:
        steps += 1

        # simple policy
        if obs["cpu"] > 70:
            action = "scale_up"
        elif obs["latency"] > 100:
            action = "restart_service"
        elif obs["memory"] > 70:
            action = "check_database"
        else:
            action = "do_nothing"

        try:
            res = requests.post(
                f"{API_BASE_URL}/step",
                json={"action": action}
            )
            data = res.json()

            obs = data["observation"]
            reward = float(data["reward"])
            done = data["done"]

            total_reward += reward

            #  STEP BLOCK (STRICT FORMAT)
            print(f"[STEP] step={steps} reward={reward}", flush=True)

        except:
            break

    #  END BLOCK (STRICT FORMAT)
    print(
        f"[END] task=incident_ai score={total_reward} steps={steps}",
        flush=True
    )


if __name__ == "__main__":
    run()