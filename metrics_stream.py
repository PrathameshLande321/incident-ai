import random

def get_metrics():
    cpu = random.randint(40, 110)
    memory = random.randint(40, 100)
    db_latency = random.randint(20, 150)

    return {
        "cpu": cpu,
        "memory": memory,
        "db_latency": db_latency
    }