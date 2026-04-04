---
title: Incident AI Resolver
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# 🚨 Incident AI Resolver

An intelligent system that **automatically detects, analyzes, and resolves infrastructure incidents** using rule-based reasoning and reward-driven optimization.

Built as a **hackathon-ready AI system** focused on:
- Real-time monitoring
- Autonomous decision-making
- Self-healing infrastructure simulation

---

# 🔥 Problem Statement

Modern systems frequently suffer from:

- ⚠️ High CPU spikes  
- ⚠️ Memory leaks  
- ⚠️ Increased latency  
- ⚠️ Service failures  

Manual debugging is:
- Slow  
- Reactive  
- Error-prone  

👉 There is a need for **automated, intelligent incident resolution systems**

---

# 💡 Solution

This project simulates an **AI-powered incident response system** that:

- Detects abnormal system behavior  
- Identifies root causes  
- Takes corrective actions  
- Optimizes decisions using rewards  

---

# ⚙️ How It Works

1. A system incident is generated (CPU / Memory / Latency)
2. The AI Agent analyzes the system state
3. It selects the best action:
   - `scale_up`
   - `restart_service`
   - `check_database`
   - `do_nothing`
4. The environment updates system metrics
5. A reward is calculated based on:
   - improvement
   - correctness
   - efficiency
6. The loop continues until the system stabilizes

---

# 🧠 Core Components

## 🔹 Agent (`agent.py`)
- Decision-making engine
- Rule-based reasoning with confidence scoring
- Outputs:
  - action
  - reason
  - confidence

---

## 🔹 Environment (`env.py`)
- Simulates real system conditions
- Applies actions and updates metrics
- Reward system includes:
  - progress reward
  - penalty for incorrect actions
  - efficiency bonus
- Stops when system is stable

---

## 🔹 Grader (`grader/`)
- Evaluates action quality
- Generates normalized score (0 → 1)

---

## 🔹 API (`api.py`)
FastAPI backend exposing endpoints:

| Endpoint | Description |
|---------|------------|
| `/set_incident` | Initialize incident scenario |
| `/live_monitor` | Run automated resolution loop |
| `/step` | Execute single action manually |

---

## 🔹 Inference (`inference.py`)
- Simulates real-world execution loop
- Calls API endpoints
- Tracks reward progression

---

# 🌐 Live Demo

Access the deployed system here:

👉 https://prathamesh-23-incident-ai.hf.space/docs

---

# 🎥 Demo Walkthrough

### Step 1: Start an Incident

POST `/set_incident`

```json
{
  "level": "hard"
}