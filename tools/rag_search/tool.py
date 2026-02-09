DEFINITION = {
    "name": "rag_knowledge_search",
    "description": "Search technical manuals and solution databases. Use this when you need to find fixes for errors.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search keywords (e.g., 'high cpu fix', 'scratch criteria')"
            }
        },
        "required": ["query"]
    }
}

async def execute(query: str):
    q = query.lower()
    docs = []
    
    # Simple keyword matching
    if "cpu" in q or "temp" in q:
        docs.append("DOC-101: High CPU usage is often caused by the 'indexer_service'. Recommended action: Restart service.")
    
    if "scratch" in q or "defect" in q:
        docs.append("DOC-205: Scratches > 1mm are critical defects. Check the polishing arm calibration.")
        
    if not docs:
        return "No relevant documents found."
        
    return "\n---\n".join(docs)