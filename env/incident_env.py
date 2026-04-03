from grader.grader import Grader
from tasks.easy_task import easy_task
from tasks.medium_task import medium_task
from tasks.hard_task import hard_task


class IncidentEnv:
    def __init__(self):
        self.task = None
        self.done = False
        self.steps = 0
        self.action_history = []
        self.grader = Grader()

    # -----------------------
    # RESET
    # -----------------------
    def reset(self, incident):
        self.done = False
        self.steps = 0
        self.action_history = []

        root = incident["root_cause"]

        if root == "high_cpu":
            self.task = easy_task()
        elif root == "db_issue":
            self.task = medium_task()
        elif root == "memory_leak":
            self.task = hard_task()
        else:
            raise ValueError("Unknown incident")

        return self._get_observation()

    # -----------------------
    # STATE (MANDATORY)
    # -----------------------
    def state(self):
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
        if self.done:
            return self._get_observation(), 0.0, True, {}

        self.steps += 1
        self.action_history.append(action)

        # -----------------------
        # STATE TRANSITION (CRITICAL FIX)
        # -----------------------
        if action == "scale_up":
            self.task["cpu"] -= 10

        elif action == "restart_service":
            self.task["latency"] -= 20

        elif action == "check_database":
            self.task["memory"] -= 10

        elif action == "do_nothing":
            pass

        # Prevent negative values (sanity)
        self.task["cpu"] = max(0, self.task["cpu"])
        self.task["memory"] = max(0, self.task["memory"])
        self.task["latency"] = max(0, self.task["latency"])

        # -----------------------
        # SCORE FROM GRADER
        # -----------------------
        score = self.grader.grade(self.task, self.action_history)

        # -----------------------
        # REWARD (TRAJECTORY BASED)
        # -----------------------
        reward = score

        # penalty for useless action
        if action == "do_nothing":
            reward -= 0.2

        # penalty for longer steps
        reward -= 0.05 * self.steps

        reward = max(0.0, reward)

        # -----------------------
        # DONE CONDITION
        # -----------------------
        if score >= 0.8 or self.steps >= 5:
            self.done = True

        # -----------------------
        # INFO
        # -----------------------
        info = {
            "score": score,
            "task": self.task["description"]
        }

        return self._get_observation(), reward, self.done, info

    # -----------------------
    # OBSERVATION (FIXED)
    # -----------------------
    def _get_observation(self):
        return {
            "cpu": self.task["cpu"],
            "memory": self.task["memory"],
            "latency": self.task["latency"],
            "steps": self.steps,
            "history": self.action_history.copy()
        }