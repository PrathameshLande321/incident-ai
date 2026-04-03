from fastapi import FastAPI
from pydantic import BaseModel
from agent import Agent
import random

app = FastAPI()
agent = Agent()

# -----------------------
# GLOBAL INCIDENT STATE
# -----------------------
current_incident = {
    "metrics": {"cpu": 90, "memory": 40, "latency": 20},
    "root_cause": "high_cpu"
}

# -----------------------
# ENVIRONMENT HELPERS (NEW)
# -----------------------
def random_state():
    return {
        "cpu": random.randint(10, 95),
        "memory": random.randint(10, 95),
        "latency": random.randint(50, 500)
    }

# -----------------------
# INPUT SCHEMAS
# -----------------------
class Metrics(BaseModel):
    cpu: int
    memory: int
    latency: int

class IncidentRequest(BaseModel):
    level: str

# ✅ NEW (for step)
class ActionInput(BaseModel):
    action: str

# -----------------------
# HOME
# -----------------------
@app.get("/")
def home():
    return {"message": "Incident AI is running"}

# -----------------------
# STATE (NEW)
# -----------------------
@app.get("/state")
def get_state():
    return current_incident["metrics"]

# -----------------------
# RESET (NEW)
# -----------------------
@app.post("/reset")
def reset():
    global current_incident
    agent.action_history = []

    current_incident["metrics"] = random_state()

    return {
        "state": current_incident["metrics"]
    }

# -----------------------
# STEP (NEW)
# -----------------------
@app.post("/step")
def step(input: ActionInput):
    global current_incident

    metrics = current_incident["metrics"]
    action = input.action

    cpu = metrics["cpu"]
    memory = metrics["memory"]
    latency = metrics["latency"]

    reward = 0.0

    # --- reward logic ---
    if cpu > 85 and latency > 250:
        reward = 1.0 if action == "restart_service" else 0.2

    elif latency > 400:
        reward = 1.0 if action == "scale_up" else 0.3

    elif memory > 85:
        reward = 1.0 if action == "clear_cache" else 0.3

    else:
        reward = 1.0 if action == "no_action" else 0.2

    # simulate next state
    current_incident["metrics"] = random_state()

    return {
        "next_state": current_incident["metrics"],
        "reward": reward,
        "done": False
    }

# -----------------------
# SET INCIDENT (UNCHANGED)
# -----------------------
@app.post("/set_incident")
def set_incident(req: IncidentRequest):
    global current_incident

    level = req.level

    agent.action_history = []

    if level == "easy":
        current_incident = {
            "metrics": {"cpu": 90, "memory": 40, "latency": 20},
            "root_cause": "high_cpu"
        }

    elif level == "medium":
        current_incident = {
            "metrics": {"cpu": 40, "memory": 50, "latency": 150},
            "root_cause": "db_issue"
        }

    elif level == "hard":
        current_incident = {
            "metrics": {"cpu": 30, "memory": 95, "latency": 200},
            "root_cause": "memory_leak"
        }

    else:
        return {"error": "Invalid level"}

    return {"message": f"Switched to {level}"}

# -----------------------
# LIVE MONITOR (UNCHANGED)
# -----------------------
@app.get("/live_monitor")
def live_monitor():
    try:
        metrics = current_incident["metrics"]
        action = agent.act(metrics)

        return {
            "metrics": metrics,
            "action": action
        }

    except Exception as e:
        return {"error": str(e)}

# -----------------------
# DIRECT PREDICT (UNCHANGED)
# -----------------------
@app.post("/predict")
def predict(metrics: Metrics):
    try:
        data = metrics.dict()
        action = agent.act(data)

        return {
            "action": action
        }

    except Exception as e:
        return {"error": str(e)}