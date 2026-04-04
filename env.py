import random


class IncidentEnv:
    def __init__(self, grader):
        self.grader = grader
        self.task = None
        self.done = False
        self.steps = 0
        self.action_history = []

    # -----------------------
    # INITIALIZE INCIDENT
    # -----------------------
    def set_task(self, task):
        self.task = task.copy()
        self.done = False
        self.steps = 0
        self.action_history = []

    # -----------------------
    # RESET (OpenEnv requirement)
    # -----------------------
    def reset(self):
        self.done = False
        self.steps = 0
        self.action_history = []
        return self._get_observation()

    # -----------------------
    # GET STATE
    # -----------------------
    def _get_observation(self):
        return {
            "cpu": self.task["cpu"],
            "memory": self.task["memory"],
            "latency": self.task["latency"],
            "steps": self.steps,
            "history": self.action_history
        }

    # -----------------------
    # SAFETY CHECK
    # -----------------------
    def _ensure_initialized(self):
        if self.task is None:
            raise ValueError("Environment not initialized. Call /set_incident first.")

    # -----------------------
    # STEP FUNCTION
    # -----------------------
    def step(self, action):
        self._ensure_initialized()

        if self.done:
            return self._get_observation(), 0.0, True, {}

        self.steps += 1
        self.action_history.append(action)

        prev_cpu = self.task["cpu"]
        prev_memory = self.task["memory"]
        prev_latency = self.task["latency"]

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

        # -----------------------
        # CONTROLLED RANDOM NOISE (REALISM BOOST)
        # -----------------------
        self.task["cpu"] += random.randint(-2, 2)
        self.task["memory"] += random.randint(-2, 2)
        self.task["latency"] += random.randint(-5, 5)

        # -----------------------
        # CLAMP VALUES (CRITICAL)
        # -----------------------
        self.task["cpu"] = max(0, min(100, self.task["cpu"]))
        self.task["memory"] = max(0, min(100, self.task["memory"]))
        self.task["latency"] = max(0, self.task["latency"])

        # -----------------------
        # PROGRESS REWARD
        # -----------------------
        improvement = (
            (prev_cpu - self.task["cpu"]) +
            (prev_memory - self.task["memory"]) +
            (prev_latency - self.task["latency"])
        )

        progress_reward = improvement / 30.0

        # -----------------------
        # GRADER SCORE
        # -----------------------
        score = self.grader.grade(self.task, self.action_history)

        # -----------------------
        # ACTION QUALITY BONUS
        # -----------------------
        correct_action_bonus = 0.0

        if self.task["cpu"] > 70 and action == "scale_up":
            correct_action_bonus += 0.2

        if self.task["latency"] > 100 and action == "restart_service":
            correct_action_bonus += 0.2

        if self.task["memory"] > 70 and action == "check_database":
            correct_action_bonus += 0.2

        # -----------------------
        # PENALTIES
        # -----------------------
        penalty = 0.0

        if action == "do_nothing":
            penalty += 0.2

        if len(self.action_history) >= 2:
            if self.action_history[-1] == self.action_history[-2]:
                penalty += 0.15

        if improvement <= 0:
            penalty += 0.25

        # -----------------------
        # EFFICIENCY BONUS
        # -----------------------
        efficiency_bonus = max(0.0, 0.3 - 0.05 * self.steps)

        # -----------------------
        # FINAL REWARD
        # -----------------------
        reward = (
            0.5 * score +
            0.3 * progress_reward +
            correct_action_bonus +
            efficiency_bonus -
            penalty
        )

        reward = max(0.0, min(1.0, reward))

        # -----------------------
        # DONE CONDITION
        # -----------------------
        if score >= 0.85 or self.steps >= 6:
            self.done = True

        # -----------------------
        # INFO
        # -----------------------
        info = {
            "score": score,
            "improvement": improvement,
            "task": self.task.get("description", "N/A")
        }

        return self._get_observation(), reward, self.done, info