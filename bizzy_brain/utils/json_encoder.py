# bizzy-gemini-version-scaffold/bizzy_brain/utils/json_encoder.py
import json
from dataclasses import is_dataclass, asdict
from enum import Enum

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        if isinstance(o, Enum):
            return o.value
        return super().default(o)
