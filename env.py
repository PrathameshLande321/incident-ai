import random

class IncidentEnv:
    def __init__(self):
        self.state = self._random_state()
        self.done = False

    def _random_state(self):
        return {
            "cpu": random.randint(10, 95),
            "memory": random.randint(10, 95),
            "latency": random.randint(50, 500)
        }

    def reset(self):
        self.state = self._random_state()
        self.done = False
        return self.state

    def get_state(self):
        return self.state

    def step(self, action):
        cpu = self.state["cpu"]
        memory = self.state["memory"]
        latency = self.state["latency"]

        # --- reward logic ---
        reward = 0

        if cpu > 85 and latency > 250:
            if action == "restart_service":
                reward = 1.0
            else:
                reward = 0.2

        elif latency > 400:
            if action == "scale_up":
                reward = 1.0
            else:
                reward = 0.3

        elif memory > 85:
            if action == "clear_cache":
                reward = 1.0
            else:
                reward = 0.3
        else:
            if action == "no_action":
                reward = 1.0
            else:
                reward = 0.2

        # simulate next state
        self.state = self._random_state()

        return {
            "next_state": self.state,
            "reward": reward,
            "done": False
        }