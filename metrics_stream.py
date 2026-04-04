import random

# 🔥 GLOBAL STATE (needed for continuity)
cpu = 50
memory = 50
db_latency = 40

def get_metrics():
    global cpu, memory, db_latency

    # 🔹 SMOOTH DRIFT (real systems don’t jump randomly)
    cpu += random.uniform(-2, 2)
    memory += random.uniform(-1.5, 1.5)
    db_latency += random.uniform(-3, 3)

    # 🔥 SPIKE EVENTS (rare but impactful)
    if random.random() < 0.12:
        cpu += random.randint(20, 35)
        db_latency += random.randint(40, 100)

    # 🔻 RECOVERY (system stabilizes over time)
    cpu -= (cpu - 55) * 0.08
    memory -= (memory - 50) * 0.05
    db_latency -= (db_latency - 45) * 0.1

    # 🔒 CLAMP VALUES (realistic bounds)
    cpu = max(10, min(cpu, 100))
    memory = max(20, min(memory, 100))
    db_latency = max(5, min(db_latency, 300))

    # 🚨 ANOMALY LOGIC
    anomaly = cpu > 85 or db_latency > 150

    # 🧠 CONFIDENCE SCORE (based on severity)
    confidence = round(
        min(1.0, (cpu / 100) * 0.6 + (db_latency / 300) * 0.4),
        2
    )

    # 🧠 REASONING ENGINE
    if anomaly:
        if cpu > 85 and db_latency > 150:
            reason = "CPU overload with database latency spike"
        elif cpu > 85:
            reason = "High CPU usage detected"
        else:
            reason = "Database latency spike detected"
    else:
        reason = "System operating within normal thresholds"

    # 🧩 MULTI-SERVICE HEALTH (still uses db_latency)
    services = [
        {
            "name": "Auth Service",
            "status": "healthy" if cpu < 80 else "critical"
        },
        {
            "name": "DB Service",
            "status": "healthy" if db_latency < 120 else "slow"
        },
        {
            "name": "API Gateway",
            "status": "healthy" if cpu < 75 else "degraded"
        },
    ]

    return {
        "metrics": {
            "cpu": round(cpu, 1),
            "memory": round(memory, 1),
            "db_latency": int(db_latency)
        },
        "anomaly": anomaly,
        "confidence": confidence,
        "reason": reason,
        "services": services
    }