from env.incident_env import IncidentEnv
from agent import Agent
import random

# -----------------------
# INCIDENTS
# -----------------------
incidents = {
    "easy": {
        "description": "CPU usage is high",
        "metrics": {"cpu": 90, "db_latency": 20, "memory": 40},
        "root_cause": "high_cpu"
    },
    "medium": {
        "description": "Database timeout",
        "metrics": {"cpu": 40, "db_latency": 150, "memory": 50},
        "root_cause": "db_issue"
    },
    "hard": {
        "description": "Memory leak",
        "metrics": {"cpu": 30, "db_latency": 20, "memory": 95},
        "root_cause": "memory_leak"
    }
}


def get_noisy_metrics(base):
    """Simulate real-world fluctuations"""
    return {
        "cpu": max(0, min(100, base["cpu"] + random.randint(-10, 10))),
        "memory": max(0, min(100, base["memory"] + random.randint(-10, 10))),
        "db_latency": max(0, base["db_latency"] + random.randint(-20, 20))
    }


def run_task(name, incident):
    print(f"\n🚀 Running task: {name}")

    # ✅ NEW ENV + AGENT PER TASK
    env = IncidentEnv()
    agent = Agent()

    # RESET ENV
    obs = env.reset(incident)

    # RESET AGENT STATE
    agent.action_history = []
    agent.last_action = None

    total_reward = 0

    for step in range(5):
        # ✅ REALISTIC METRICS (NOT STATIC)
        metrics = get_noisy_metrics(incident["metrics"])

        # agent decision
        action, info_agent = agent.act(metrics)

        # env step (NEW FORMAT)
        obs, reward, done, info_env = env.step(action)

        total_reward += reward

        print(
            f"Step {step+1}: "
            f"action={action}, "
            f"reward={round(reward,2)}, "
            f"done={done}, "
            f"score={round(info_env['score'],2)}"
        )

        if done:
            break

    # -----------------------
    # FINAL SCORE (CORRECT)
    # -----------------------
    final_score = env.grader.grade(env.task, env.action_history)

    print(f"✅ Final Score ({name}): {final_score:.2f}")

    return final_score


# -----------------------
# RUN ALL TASKS
# -----------------------
if __name__ == "__main__":
    results = {}

    # optional reproducibility
    random.seed(42)

    for name, incident in incidents.items():
        score = run_task(name, incident)
        results[name] = score

    print("\n📊 FINAL RESULTS")
    for k, v in results.items():
        print(f"{k}: {v:.2f}")

    avg = sum(results.values()) / len(results)
    print(f"\n🔥 Average Score: {avg:.2f}")