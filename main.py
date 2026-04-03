from fastapi import FastAPI
from env.incident_env import IncidentEnv
from agent import Agent
from metrics_stream import get_metrics

# ✅ NEW IMPORTS (OpenEnv spec)
from models import Observation, StepResponse, ResetResponse

app = FastAPI(title="Incident AI Resolver")

env = IncidentEnv()
agent = Agent()

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
# RESET (OpenEnv compliant)
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
# STEP (OpenEnv compliant)
# -----------------------
@app.post("/step", response_model=StepResponse)
def step(action: str):
    # ensure env initialized
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
# AUTO PLAY (optional)
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
# LIVE MONITOR (OpenEnv format)
# -----------------------
@app.get("/live_monitor", response_model=StepResponse)
def live_monitor():
    try:
        # ensure env initialized
        if env.incident is None:
            env.reset(current_incident)

        # fetch metrics
        metrics = get_metrics()
        print("🔥 METRICS DEBUG:", metrics)

        if metrics is None or not isinstance(metrics, dict):
            raise ValueError("Invalid metrics")

        # agent decision
        action, info = agent.act(metrics)

        print("ACTION:", action)
        print("INFO:", info)

        # env step
        reward, done = env.step(action)

        # learning
        agent.learn(action, reward)

        # observation
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
        print("ERROR IN /live_monitor:", e)
        return StepResponse(
            observation=Observation(cpu=0, memory=0, db_latency=0),
            reward=0.0,
            done=True,
            info={"error": str(e)}
        )