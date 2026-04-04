from grader.grader import Grader
from tasks.easy_task import easy_task
from tasks.medium_task import medium_task
from tasks.hard_task import hard_task


class IncidentEnv:
    def __init__(self):
        self.task = None
        self.incident = None
        self.done = False
        self.steps = 0
        self.action_history = []
        self.grader = Grader()

    # -----------------------
    # RESET (MANDATORY ENTRY POINT)
    # -----------------------
    def reset(self, incident):
        if not incident or "root_cause" not in incident:
            raise ValueError("Invalid incident input")

        self.done = False
        self.steps = 0
        self.action_history = []
        self.incident = incident

        root = incident["root_cause"]

        if root == "high_cpu":
            self.task = easy_task()
        elif root == "db_issue":
            self.task = medium_task()
        elif root == "memory_leak":
            self.task = hard_task()
        else:
            raise ValueError(f"Unknown incident type: {root}")

        return self._get_observation()

    # -----------------------
    # SAFETY CHECK
    # -----------------------
    def _ensure_initialized(self):
        if self.task is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")

    # -----------------------
    # STATE
    # -----------------------
    def state(self):
        self._ensure_initialized()

        return {
            "cpu": self.task["cpu"],
            "memory": self.task["memory"],
            "latency": self.task["latency"],
            "steps": self.steps,
            "history": self.action_history.copy()
        }

    # -----------------------
    # STEP
    # -----------------------
    def step(self, action):
        self._ensure_initialized()

        if self.done:
            return self._get_observation(), 0.0, True, {}

        self.steps += 1
        self.action_history.append(action)

        # -----------------------
        # STATE TRANSITION
        # -----------------------
        if action == "scale_up":
            self.task["cpu"] -= 10

        elif action == "restart_service":
            self.task["latency"] -= 20

        elif action == "check_database":
            self.task["memory"] -= 10

        elif action == "do_nothing":
            pass

        else:
            raise ValueError(f"Invalid action: {action}")

        # Clamp values
        self.task["cpu"] = max(0, self.task["cpu"])
        self.task["memory"] = max(0, self.task["memory"])
        self.task["latency"] = max(0, self.task["latency"])

        # -----------------------
        # GRADING
        # -----------------------
        score = self.grader.grade(self.task, self.action_history)

        reward = score

        if action == "do_nothing":
            reward -= 0.2

        reward -= 0.05 * self.steps
        reward = max(0.0, reward)

        # -----------------------
        # DONE CONDITION
        # -----------------------
        if score >= 0.8 or self.steps >= 5:
            self.done = True

        info = {
            "score": score,
            "task": self.task.get("description", "N/A")
        }

        return self._get_observation(), reward, self.done, info

    # -----------------------
    # OBSERVATION
    # -----------------------
    def _get_observation(self):
        self._ensure_initialized()

        return {
            "cpu": self.task["cpu"],
            "memory": self.task["memory"],
            "latency": self.task["latency"],
            "steps": self.steps,
            "history": self.action_history.copy()
        }