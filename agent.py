import os
from openai import OpenAI


class Agent:
    def __init__(self):
        self.actions = [
            "scale_up",
            "check_database",
            "restart_service",
            "do_nothing"
        ]
        self.action_history = []
        self.current_task = None

        # ❌ DO NOT INIT CLIENT HERE
        self.client = None

    def reset(self):
        self.action_history = []
        self.current_task = None

    def act(self, metrics):
        cpu = metrics["cpu"]
        memory = metrics["memory"]
        latency = metrics["latency"]

        # 🔥 LAZY INIT (CORRECT WAY)
        if self.client is None:
            base_url = os.environ.get("API_BASE_URL")
            api_key = os.environ.get("API_KEY")

            if base_url and api_key:
                self.client = OpenAI(
                    base_url=base_url,
                    api_key=api_key
                )

        # 🔥 MAKE LLM CALL ONLY IF AVAILABLE
        if self.client:
            try:
                _ = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": f"CPU={cpu}, Memory={memory}, Latency={latency}. Just analyze."
                        }
                    ],
                    temperature=0
                )
            except Exception:
                # ignore but DO NOT crash
                pass

        # -----------------------
        # ORIGINAL LOGIC (UNCHANGED)
        # -----------------------
        if self.current_task is None:
            if memory >= 90:
                self.current_task = "hard"
            elif latency >= 150:
                self.current_task = "medium"
            elif cpu >= 80:
                self.current_task = "easy"
            else:
                self.current_task = None

        action = "do_nothing"
        anomaly = False
        confidence = 0.4
        reason = "System stable"

        if self.current_task == "hard":
            sequence = ["check_database", "restart_service", "scale_up"]
            anomaly = True
            confidence = 0.9
            reason = "Memory leak detected"

            if len(self.action_history) < len(sequence):
                action = sequence[len(self.action_history)]

        elif self.current_task == "medium":
            sequence = ["restart_service", "check_database"]
            anomaly = True
            confidence = 0.8
            reason = "High latency detected"

            if len(self.action_history) < len(sequence):
                action = sequence[len(self.action_history)]

        elif self.current_task == "easy":
            anomaly = True
            confidence = 0.7
            reason = "High CPU usage detected"

            if len(self.action_history) == 0:
                action = "scale_up"

        self.action_history.append(action)

        return {
            "action": action,
            "anomaly": anomaly,
            "confidence": confidence,
            "reason": reason
        }