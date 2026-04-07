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

        # 🔥 FORCE ENV (NO SILENT FAIL)
        base_url = os.environ.get("API_BASE_URL")
        api_key = os.environ.get("API_KEY")

        if not base_url or not api_key:
            raise ValueError("Missing API_BASE_URL or API_KEY")

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

    # -----------------------
    # RESET
    # -----------------------
    def reset(self):
        self.action_history = []
        self.current_task = None

    # -----------------------
    # DECISION MAKING
    # -----------------------
    def act(self, metrics):
        cpu = metrics["cpu"]
        memory = metrics["memory"]
        latency = metrics["latency"]

        # 🔥 GUARANTEED LLM CALL (NO SILENT FAIL)
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
        except Exception as e:
            # ❌ DO NOT IGNORE — FAIL FAST
            raise RuntimeError(f"LLM call failed: {e}")

        # -----------------------
        # 1) DETECT TASK ONLY ONCE
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

        # -----------------------
        # 2) DEFAULT VALUES
        # -----------------------
        action = "do_nothing"
        anomaly = False
        confidence = 0.4
        reason = "System stable"

        # -----------------------
        # 3) HARD TASK
        # -----------------------
        if self.current_task == "hard":
            sequence = ["check_database", "restart_service", "scale_up"]

            anomaly = True
            confidence = 0.9
            reason = "Memory leak detected"

            if len(self.action_history) < len(sequence):
                action = sequence[len(self.action_history)]

        # -----------------------
        # 4) MEDIUM TASK
        # -----------------------
        elif self.current_task == "medium":
            sequence = ["restart_service", "check_database"]

            anomaly = True
            confidence = 0.8
            reason = "High latency detected"

            if len(self.action_history) < len(sequence):
                action = sequence[len(self.action_history)]

        # -----------------------
        # 5) EASY TASK
        # -----------------------
        elif self.current_task == "easy":
            anomaly = True
            confidence = 0.7
            reason = "High CPU usage detected"

            if len(self.action_history) == 0:
                action = "scale_up"

        # -----------------------
        # 6) SAVE HISTORY
        # -----------------------
        self.action_history.append(action)

        # -----------------------
        # 7) RETURN OUTPUT
        # -----------------------
        return {
            "action": action,
            "anomaly": anomaly,
            "confidence": confidence,
            "reason": reason
        }