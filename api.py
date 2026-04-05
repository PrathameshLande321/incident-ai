from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import asyncio
import os
import random

from agent import Agent
from env import IncidentEnv
from grader.grader import Grader

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
grader = Grader()
env = IncidentEnv(grader)

current_obs = None

# -----------------------
# INPUT SCHEMA
# -----------------------
class IncidentRequest(BaseModel):
    level: str

class ActionInput(BaseModel):
    action: str


# -----------------------
# ROOT
# -----------------------
@app.get("/")
def serve_ui():
    file_path = os.path.join(os.getcwd(), "index.html")
    if not os.path.exists(file_path):
        return {"error": "index.html not found"}
    return FileResponse(file_path)


# =========================================================
# ✅ OPENENV REQUIRED ENDPOINTS (FINAL FIX)
# =========================================================

@app.post("/reset")
def reset():
    global current_obs

    try:
        agent.reset()

        # 🔥 RANDOMIZE TASK (IMPORTANT)
        task = random.choice([
            easy_task(),
            medium_task(),
            hard_task()
        ])

        env.set_task(task)
        current_obs = env.reset()

        return {
            "observation": current_obs,
            "reward": 0.0,
            "done": False,
            "info": {}
        }

    except Exception as e:
        return {
            "observation": {},
            "reward": 0.0,
            "done": True,
            "info": {"error": str(e)}
        }


@app.post("/step")
def step_openenv(action: ActionInput):
    global current_obs

    try:
        if current_obs is None:
            return {
                "observation": {},
                "reward": 0.0,
                "done": True,
                "info": {"error": "reset not called"}
            }

        obs, reward, done, info = env.step(action.action)
        current_obs = obs

        return {
            "observation": obs,
            "reward": float(reward),   # 🔥 enforce float
            "done": bool(done),       # 🔥 enforce bool
            "info": info if isinstance(info, dict) else {}
        }

    except Exception as e:
        return {
            "observation": current_obs if current_obs else {},
            "reward": 0.0,
            "done": True,
            "info": {"error": str(e)}
        }


# =========================================================
# 🔵 YOUR EXISTING UI (UNCHANGED)
# =========================================================

@app.post("/set_incident")
def set_incident(req: IncidentRequest):
    global current_obs

    agent.reset()

    if req.level == "easy":
        task = easy_task()
    elif req.level == "medium":
        task = medium_task()
    elif req.level == "hard":
        task = hard_task()
    else:
        return {"error": "Invalid level"}

    env.set_task(task)
    current_obs = env.reset()

    return {
        "message": f"{req.level} incident started",
        "observation": current_obs
    }


@app.post("/step_internal")
def step_internal():
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