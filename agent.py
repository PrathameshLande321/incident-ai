class Agent:
    def __init__(self):
        self.actions = [
            "scale_up",
            "check_database",
            "restart_service",
            "do_nothing"
        ]
        self.action_history = []
        self.current_task = None  # "hard" | "medium" | "easy" | None

    # -----------------------
    # DECISION MAKING
    # -----------------------
    def act(self, metrics):
        cpu = metrics["cpu"]
        memory = metrics["memory"]
        latency = metrics["latency"]

        # -----------------------
        # 1) Detect task ONCE
        # -----------------------
        if len(self.action_history) == 0:
            if memory >= 90:
                self.current_task = "hard"
            elif latency >= 150:
                self.current_task = "medium"
            elif cpu >= 80:
                self.current_task = "easy"
            else:
                self.current_task = None

        # -----------------------
        # 2) HARD TASK (3-step sequence)
        # check_database → restart_service → scale_up
        # -----------------------
        if self.current_task == "hard":
            if len(self.action_history) == 0:
                return self._finalize("check_database")

            if self.action_history[-1] == "check_database":
                return self._finalize("restart_service")

            if self.action_history[-1] == "restart_service":
                return self._finalize("scale_up")

            return self._finalize("do_nothing")

        # -----------------------
        # 3) MEDIUM TASK (2-step sequence)
        # restart_service → check_database
        # -----------------------
        if self.current_task == "medium":
            if len(self.action_history) == 0:
                return self._finalize("restart_service")

            if self.action_history[-1] == "restart_service":
                return self._finalize("check_database")

            return self._finalize("do_nothing")

        # -----------------------
        # 4) EASY TASK (1-step)
        # -----------------------
        if self.current_task == "easy":
            if len(self.action_history) == 0:
                return self._finalize("scale_up")

            return self._finalize("do_nothing")

        # -----------------------
        # 5) FALLBACK
        # -----------------------
        return self._finalize("do_nothing")

    # -----------------------
    # FINALIZE ACTION
    # -----------------------
    def _finalize(self, action):
        self.action_history.append(action)
        return action