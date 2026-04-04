from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware   # ✅ ADDED
from fastapi.responses import JSONResponse           # ✅ ADDED

from env import IncidentEnv
from agent import Agent
from metrics_stream import get_metrics

from models import Observation, StepResponse, ResetResponse

app = FastAPI(title="Incident AI Resolver")

# ✅ CORS FIX (REQUIRED)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = IncidentEnv()
agent = Agent()

# -----------------------
# ROOT (REQUIRED FOR HF)
# -----------------------
@app.get("/")
def home():
    return JSONResponse(content={"status": "running", "message": "API is live 🚀"})

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
        "description": "Database connection timeout errors",
        "metrics": {"cpu": 40, "db_latency": 150, "memory": 50},
        "root_cause": "db_issue"
    },
    "hard": {
        "description": "Memory usage increasing continuously",
        "metrics": {"cpu": 30, "db_latency": 20, "memory": 95},
        "root_cause": "memory_leak"
    }
}

current_incident = incidents["easy"]

# -----------------------
# INCIDENT SWITCH
# -----------------------
@app.get("/set_incident")
def set_incident(level: str):
    global current_incident

    if level not in incidents:
        return {"error": "invalid level"}

    current_incident = incidents[level]
    return {"message": f"Switched to {level}"}

# -----------------------
# RESET
# -----------------------
@app.get("/reset", response_model=ResetResponse)
def reset():
    env.reset(current_incident)

    obs = Observation(
        cpu=current_incident["metrics"]["cpu"],
        memory=current_incident["metrics"]["memory"],
        db_latency=current_incident["metrics"]["db_latency"]
    )

    return ResetResponse(observation=obs)

# -----------------------
# STEP
# -----------------------
@app.post("/step", response_model=StepResponse)
def step(action: str):
    if env.incident is None:
        env.reset(current_incident)

    metrics = get_metrics()
    reward, done = env.step(action)

    obs = Observation(
        cpu=metrics["cpu"],
        memory=metrics["memory"],
        db_latency=metrics["db_latency"]
    )

    return StepResponse(
        observation=obs,
        reward=reward,
        done=done,
        info={"action": action}
    )

# -----------------------
# AUTO PLAY
# -----------------------
@app.get("/auto_play")
def auto_play():
    actions_taken = []

    try:
        env.reset(current_incident)

        for _ in range(5):
            metrics = get_metrics()
            action, scores = agent.act(metrics)

            reward, done = env.step(action)
            agent.learn(action, reward)

            actions_taken.append({
                "metrics": metrics,
                "action": action,
                "scores": scores,
                "reward": reward
            })

        return {
            "simulation": actions_taken,
            "memory": agent.memory
        }

    except Exception as e:
        return {"error": str(e)}

# -----------------------
# LIVE MONITOR
# -----------------------
@app.get("/live_monitor")
def live_monitor():
    try:
        if env.incident is None:
            env.reset(current_incident)

        metrics = get_metrics()

        if metrics is None or not isinstance(metrics, dict):
            raise ValueError("Invalid metrics")

        action, info = agent.act(metrics)

        reward, done = env.step(action)
        agent.learn(action, reward)

        obs = Observation(
            cpu=metrics["cpu"],
            memory=metrics["memory"],
            db_latency=metrics["db_latency"]
        )

        return StepResponse(
            observation=obs,
            reward=reward,
            done=done,
            info={
                "action": action,
                "reason": info.get("reason"),
                "confidence": info.get("confidence")
            }
        )

    except Exception as e:
        return StepResponse(
            observation=Observation(cpu=0, memory=0, db_latency=0),
            reward=0.0,
            done=True,
            info={"error": str(e)}
        )

# -----------------------
# WEBSOCKET (REQUIRED FOR FRONTEND)
# -----------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            if env.incident is None:
                env.reset(current_incident)

            metrics = get_metrics()
            action, info = agent.act(metrics)

            reward, done = env.step(action)

            data = {
                "metrics": metrics,
                "action": action,
                "anomaly": metrics["cpu"] > 85 or metrics["db_latency"] > 300,
                "confidence": info.get("confidence"),
                "reason": info.get("reason"),
            }

            await websocket.send_json(data)

            import asyncio
            await asyncio.sleep(1)

    except Exception:
        pass