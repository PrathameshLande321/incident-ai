import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

ACTIONS = [
    "scale_up",
    "restart_service",
    "check_database",
    "do_nothing"
]


def run():
    print("START")

    total_reward = 0.0
    steps = 0

    # -----------------------
    # RESET ENV (MANDATORY)
    # -----------------------
    try:
        res = requests.post(f"{API_BASE_URL}/reset")
        data = res.json()

        if "error" in data or "detail" in data:
            raise Exception(data)

        obs = data["observation"]
        done = data["done"]

        print(f"RESET → {obs}")

    except Exception as e:
        print(f"RESET FAILED → {e}")
        print("END total_reward=0.00")
        return {"total_reward": 0.0, "steps": 0}

    # -----------------------
    # LOOP
    # -----------------------
    while not done and steps < 10:
        steps += 1

        # 🔥 SIMPLE POLICY (IMPORTANT)
        # Choose action based on state
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

            print(
                f"STEP {steps}: action={action}, reward={reward:.2f}, done={done}"
            )

        except Exception as e:
            print(f"STEP {steps}: FAILED → {e}")
            break

    print(f"END total_reward={total_reward:.2f}")

    return {
        "total_reward": total_reward,
        "steps": steps
    }


if __name__ == "__main__":
    print(run())