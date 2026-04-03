from pydantic import BaseModel
from typing import Dict

# ---------------------------
# OBSERVATION (state)
# ---------------------------
class Observation(BaseModel):
    cpu: float
    memory: float
    db_latency: float


# ---------------------------
# ACTION
# ---------------------------
class Action(BaseModel):
    action: str  # scale_up, check_database, restart_service, do_nothing


# ---------------------------
# STEP RESPONSE (OpenEnv spec)
# ---------------------------
class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict


# ---------------------------
# RESET RESPONSE
# ---------------------------
class ResetResponse(BaseModel):
    observation: Observation