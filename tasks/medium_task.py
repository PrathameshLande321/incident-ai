def medium_task():
    return {
        "description": "Fix database latency issue",
        "cpu": 40,
        "memory": 50,
        "latency": 180,
        "solution": ["restart_service", "check_database"]
    }