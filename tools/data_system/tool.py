DEFINITION = {
    "name": "surface_defect_lookup",
    "description": "Check product quality by Image ID. Returns defect type and severity from database.",
    "input_schema": {
        "type": "object",
        "properties": {
            "image_id": {
                "type": "string",
                "description": "The ID of the image or product batch (e.g., 'IMG_001')"
            }
        },
        "required": ["image_id"]
    }
}

# Mock Database
MOCK_DB = {
    "IMG_001": {"defects": [], "status": "pass"},
    "IMG_002": {"defects": ["scratch_2mm", "discoloration"], "status": "reject", "severity": "high"},
    "IMG_003": {"defects": ["minor_dent"], "status": "review", "severity": "low"}
}

async def execute(image_id: str):
    result = MOCK_DB.get(image_id, {"error": "Image ID not found in database"})
    return {"image_id": image_id, "analysis_result": result}