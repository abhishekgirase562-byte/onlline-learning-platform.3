from datetime import datetime
from bson import ObjectId

def serialize_doc(doc):
    """
    Recursively serialize MongoDB documents converting ObjectId and datetime to JSON-serializable types.
    """
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if key == "_id":
                result["id"] = str(value)
                result["_id"] = str(value)
            elif isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, (dict, list)):
                result[key] = serialize_doc(value)
            else:
                result[key] = value
        return result
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, datetime):
        return doc.isoformat()
    return doc


def to_object_id(id_str):
    """
    Safely converts a string to an ObjectId. If it's already an ObjectId or invalid, handles gracefully.
    """
    if isinstance(id_str, ObjectId):
        return id_str
    try:
        return ObjectId(str(id_str))
    except Exception:
        return None
