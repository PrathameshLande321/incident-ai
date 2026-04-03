def medium_task():
    return {
        "description": "Fix database latency issue",
        "cpu": 75,
        "memory": 70,
        "latency": 160,
        "solution": ["restart_service", "check_database"]
    }