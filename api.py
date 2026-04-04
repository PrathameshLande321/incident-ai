from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

from agent import Agent
from env import IncidentEnv
from grader.grader import Grader   # ✅ REQUIRED

from tasks.easy_task import easy_task
from tasks.medium_task import medium_task
from tasks.hard_task import hard_task

app = FastAPI()

# -----------------------
# CORS
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# GLOBAL SYSTEM
# -----------------------
agent = Agent()

grader = Grader()                  # ✅ FIX
env = IncidentEnv(grader)          # ✅ FIX

current_obs = None

# -----------------------
# INPUT SCHEMA
# -----------------------
class IncidentRequest(BaseModel):
    level: str


# -----------------------
# ROOT
# -----------------------
@app.get("/")
def home():
    return {"status": "running", "mode": "env-integrated"}


# -----------------------
# SET INCIDENT
# -----------------------
@app.post("/set_incident")
def set_incident(req: IncidentRequest):
    global current_obs

    agent.reset()

    # -----------------------
    # LOAD TASK PROPERLY
    # -----------------------
    if req.level == "easy":
        task = easy_task()
    elif req.level == "medium":
        task = medium_task()
    elif req.level == "hard":
        task = hard_task()
    else:
        return {"error": "Invalid level"}

    # -----------------------
    # INIT ENV CORRECTLY
    # -----------------------
    env.set_task(task)        # ✅ REQUIRED
    current_obs = env.reset() # ✅ REQUIRED

    return {
        "message": f"{req.level} incident started",
        "observation": current_obs
    }


# -----------------------
# STEP
# -----------------------
@app.post("/step")
def step():
    global current_obs

    if current_obs is None:
        return {"error": "Call /set_incident first"}

    decision = agent.act(current_obs)
    action = decision["action"]

    obs, reward, done, info = env.step(action)
    current_obs = obs

    return {
        "observation": obs,
        "action": action,
        "reward": reward,
        "done": done,
        "score": info.get("score", 0),
        "reason": decision["reason"],
        "confidence": decision["confidence"]
    }


# -----------------------
# LIVE MONITOR
# -----------------------
@app.get("/live_monitor")
def live_monitor():
    global current_obs

    if current_obs is None:
        return {"error": "Initialize with /set_incident"}

    decision = agent.act(current_obs)
    action = decision["action"]

    obs, reward, done, info = env.step(action)
    current_obs = obs

    return {
        "observation": obs,
        "action": action,
        "reward": reward,
        "done": done,
        "score": info.get("score", 0),
        "reason": decision["reason"],
        "confidence": decision["confidence"]
    }


# -----------------------
# WEBSOCKET
# -----------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    global current_obs

    if current_obs is None:
        task = easy_task()
        env.set_task(task)
        current_obs = env.reset()
        agent.reset()

    try:
        while True:
            decision = agent.act(current_obs)
            action = decision["action"]

            obs, reward, done, info = env.step(action)
            current_obs = obs

            await websocket.send_json({
                "observation": obs,
                "action": action,
                "reward": reward,
                "done": done,
                "score": info.get("score", 0),
                "reason": decision["reason"],
                "confidence": decision["confidence"]
            })

            if done:
                task = easy_task()
                env.set_task(task)
                current_obs = env.reset()
                agent.reset()

            await asyncio.sleep(1)

    except Exception as e:
        print("WebSocket error:", e)