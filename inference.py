import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

def run():
    task_name = "incident_ai"

    total_reward = 0.0
    steps = 0

    # -----------------------
    # START BLOCK (REQUIRED)
    # -----------------------
    print(f"[START] task={task_name}", flush=True)

    # -----------------------
    # RESET ENV
    # -----------------------
    try:
        res = requests.post(f"{API_BASE_URL}/reset")
        data = res.json()

        if "error" in data or "detail" in data:
            raise Exception(data)

        obs = data["observation"]
        done = data["done"]

    except Exception:
        # MUST still print END block
        print(f"[END] task={task_name} score=0 steps=0", flush=True)
        return

    # -----------------------
    # LOOP
    # -----------------------
    while not done and steps < 10:
        steps += 1

        # SIMPLE POLICY
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

            if "error" in data:
                raise Exception(data)

            obs = data["observation"]
            reward = float(data["reward"])
            done = data["done"]

            total_reward += reward

            # -----------------------
            # STEP BLOCK (REQUIRED)
            # -----------------------
            print(
                f"[STEP] step={steps} reward={reward}",
                flush=True
            )

        except Exception:
            break

    # -----------------------
    # END BLOCK (REQUIRED)
    # -----------------------
    print(
        f"[END] task={task_name} score={total_reward} steps={steps}",
        flush=True
    )


if __name__ == "__main__":
    run()