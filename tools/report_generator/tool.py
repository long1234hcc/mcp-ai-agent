DEFINITION = {
    "name": "generate_report",
    "description": "Generate a summary report text based on provided data.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "content": {"type": "string"}
        },
        "required": ["title", "content"]
    }
}

async def execute(title: str, content: str):
    filename = f"report_{title.replace(' ', '_')}.txt"
    # Trong thực tế sẽ ghi file, ở đây chỉ return message
    return f"Report '{filename}' generated successfully. Content length: {len(content)} chars."