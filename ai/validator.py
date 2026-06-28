import json
import logging
from typing import List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ExtractedEntitiesDTO(BaseModel):
    victim: Optional[str] = None
    accused: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    crime_type: Optional[str] = None
    vehicles: List[str] = Field(default_factory=list)
    weapons: List[str] = Field(default_factory=list)
    stolen_items: List[str] = Field(default_factory=list)
    sections: List[str] = Field(default_factory=list)
    summary: Optional[str] = None


class ExtractionError(Exception):
    pass


def parse_and_validate(json_str: str) -> ExtractedEntitiesDTO:
    """Parses a JSON string and validates it against the ExtractedEntitiesDTO schema."""
    try:
        # Strip markdown formatting if present
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]

        data = json.loads(json_str.strip())

        if isinstance(data.get("time"), list):
            data["time"] = ", ".join(map(str, data["time"]))

        for field in ["vehicles", "weapons", "stolen_items", "sections"]:
            if field in data and isinstance(data[field], list):
                new_list = []
                for item in data[field]:
                    if isinstance(item, dict):
                        new_list.append(", ".join([f"{k}: {v}" for k, v in item.items()]))
                    elif isinstance(item, list):
                        new_list.append(", ".join(map(str, item)))
                    else:
                        new_list.append(str(item))
                data[field] = new_list

        dto = ExtractedEntitiesDTO(**data)
        return dto
    except json.JSONDecodeError as e:
        logger.error(f"JSON Parsing Error: {e}")
        raise ExtractionError(f"Invalid JSON format: {e}")
    except Exception as e:
        logger.error(f"Validation Error: {e}")
        raise ExtractionError(f"Data validation failed: {e}")
