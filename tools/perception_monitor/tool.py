import random

DEFINITION = {
    "name": "perception_monitor",
    "description": "Get real-time system metrics (CPU, Memory, Temperature). Use this to check system health.",
    "input_schema": {
        "type": "object",
        "properties": {
            "target": {
                "type": "string", 
                "description": "Target system ID (e.g., 'main_server', 'robot_arm')",
                "default": "main_server"
            }
        }
    }
}

async def execute(target: str = "main_server"):
    # Mock data: Random CPU & Temp
    cpu = random.randint(20, 95) 
    temp = random.randint(40, 80)
    
    status = "healthy"
    if cpu > 80 or temp > 75:
        status = "warning"
        
    return {
        "target": target,
        "status": status,
        "metrics": {
            "cpu_usage": f"{cpu}%",
            "memory_usage": "45%",
            "temperature": f"{temp}C"
        }
    }