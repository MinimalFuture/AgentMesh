import json


def json_loads(text: str):
    """
    Deserialize a JSON string
    
    :param text: The JSON string to be deserialized.
    :return: The deserialized Python object.
    """
    if text.startswith("```json") and text.endswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
    return json.loads(text.strip())


