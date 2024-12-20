import json

def extract_mention_data(content: str, trigger: str):
    """
    Extracts 'data.id' and 'data.avatar' from beautifulMention nodes with the specified trigger.
    
    Args:
        content (str): The JSON string containing the content.
        trigger (str): The trigger to filter mentions (e.g., '@').
    
    Returns:
        list: A list of dictionaries containing 'id' and 'avatar' for matching mentions.
    """
    mention_data = []
    
    try:
        content_dict = json.loads(content)
        
        def traverse(node):
            if isinstance(node, dict):
                if node.get("type") == "beautifulMention" and node.get("trigger") == trigger:
                    data = node.get("data", {})
                    mention_data.append({
                        "id": data.get("id"),
                        "avatar": data.get("avatar")
                    })
                for key, value in node.items():
                    traverse(value)
            elif isinstance(node, list):
                for item in node:
                    traverse(item)
        
        traverse(content_dict)
    
    except json.JSONDecodeError as e:
        print(f"Invalid JSON content: {e}")
    
    return mention_data