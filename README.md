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

An intelligent system that **automatically detects, analyzes, and resolves infrastructure incidents** using rule-based decision logic and reward-driven optimization.

Built for hackathon submission with a focus on **real-time monitoring, decision-making, and automated recovery**.

---

# 🔥 Problem Statement

Modern systems frequently face:
- High CPU spikes
- Memory leaks
- Increased latency
- Service failures

Manual debugging is slow, reactive, and inefficient.

👉 This project introduces an **AI-driven automated incident resolution system**.

---

# ⚙️ How It Works

1. System generates a simulated incident (CPU / Memory / Latency)
2. Agent analyzes current state
3. Best action is selected:
   - scale_up
   - restart_service
   - check_database
   - do_nothing
4. Environment updates system state
5. Reward is calculated based on:
   - improvement
   - correctness
   - efficiency
6. Loop continues until system stabilizes

---

# 🧠 Core Components

## 1. Agent (`agent.py`)
- Decision-making engine
- Uses rule-based reasoning
- Outputs:
  - action
  - reason
  - confidence

---

## 2. Environment (`env.py`)
- Simulates infrastructure metrics
- Applies actions and updates state
- Reward system includes:
  - progress reward
  - penalty for wrong actions
  - efficiency bonus
- Terminates when resolved

---

## 3. Grader (`grader/`)
- Evaluates action correctness
- Produces normalized score (0 → 1)

---

## 4. API (`api.py`)
FastAPI backend powering the system:

| Endpoint | Purpose |
|--------|--------|
| `/set_incident` | Initialize incident |
| `/live_monitor` | Automatic resolution loop |
| `/step` | Manual step execution |

---

## 5. Inference (`inference.py`)
- Simulates real-world execution
- Calls API endpoints
- Tracks reward and performance

---

# 🚀 Features

- Real-time incident simulation
- Intelligent decision-making agent
- Reward-based optimization
- REST API + WebSocket support
- Fully Dockerized deployment
- Hugging Face Spaces ready

---

# 📊 Example Flow

```text
CPU: 90 → scale_up → 70
Memory: 85 → check_database → 75
Latency: 200 → restart_service → 120
System stabilized → done