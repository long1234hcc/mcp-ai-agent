DEFINITION = {
    "name": "external_api_connector",
    "description": "Send alerts or notifications to external systems (Slack, Email).",
    "input_schema": {
        "type": "object",
        "properties": {
            "message": {"type": "string"},
            "severity": {"type": "string", "enum": ["info", "warning", "critical"]}
        },
        "required": ["message"]
    }
}

async def execute(message: str, severity: str = "info"):
    print(f"🚀 [EXTERNAL API] Sending {severity.upper()} alert: {message}")
    return {"status": "sent", "timestamp": "2024-02-09T12:00:00Z"}