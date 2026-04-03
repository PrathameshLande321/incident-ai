from env.incident_env import IncidentEnv
from agent import Agent
from grader.grader import Grader


def run_task(task_name, incident):
    print(f"\n===== RUNNING TASK: {task_name.upper()} =====")

    env = IncidentEnv()
    agent = Agent()
    grader = Grader()

    obs = env.reset(incident)

    print("Initial Observation:", obs)

    done = False

    while not done:
        action = agent.act(obs)   # agent decides
        obs, reward, done, info = env.step(action)

        print(f"\nStep: {obs['steps']}")
        print("Action:", action)
        print("Reward:", reward)
        print("State:", obs)
        print("Info:", info)

    final_score = grader.grade(env.task, env.action_history)

    print("\n===== FINAL RESULT =====")
    print("Final Score:", final_score)
    print("Actions Taken:", env.action_history)


if __name__ == "__main__":

    # EASY
    run_task(
        "easy",
        {"root_cause": "high_cpu"}
    )

    # MEDIUM
    run_task(
        "medium",
        {"root_cause": "db_issue"}
    )

    # HARD
    run_task(
        "hard",
        {"root_cause": "memory_leak"}
    )