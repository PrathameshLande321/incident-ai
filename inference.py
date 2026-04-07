import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def run():
    total_reward = 0.0
    steps = 0

    # START BLOCK
    print("[START] task=incident_ai", flush=True)

    try:
        res = requests.post(f"{API_BASE_URL}/reset")
        data = res.json()

        obs = data.get("observation", {})

        # 🔥 FORCE LOOP START (CRITICAL FIX)
        done = False

    except:
        print("[END] task=incident_ai score=0 steps=0", flush=True)
        return

    while steps < 10:   # 🔥 REMOVE dependency on initial done
        steps += 1

        # safety check (avoid crash)
        if not obs:
            break

        # simple policy
        if obs.get("cpu", 0) > 70:
            action = "scale_up"
        elif obs.get("latency", 0) > 100:
            action = "restart_service"
        elif obs.get("memory", 0) > 70:
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

            # STEP BLOCK
            print(f"[STEP] step={steps} reward={reward}", flush=True)

            # 🔥 BREAK ONLY AFTER AT LEAST 1 STEP
            if done:
                break

        except:
            break

    # END BLOCK
    print(
        f"[END] task=incident_ai score={total_reward} steps={steps}",
        flush=True
    )


if __name__ == "__main__":
    run()