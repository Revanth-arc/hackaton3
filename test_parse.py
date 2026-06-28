import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai.validator import parse_and_validate

test_json = """
{
  "victim": "unknown",
  "accused": "",
  "date": "28-06-2026",
  "time": "",
  "location": "",
  "crime_type": "theft",
  "vehicles": [
    {
      "make": "Bajaj Pulsar Ns",
      "n_number": "TS09AB4587"
    }
  ],
  "weapons": [],
  "stolen_items": [
    {
      "item": "Riding helmet",
      "value": 5000
    },
    {
      "item": "Personal documents",
      "value": null
    }
  ],
  "sections": [],
  "summary": ""
}
"""
try:
    dto = parse_and_validate(test_json)
    print("Success:")
    print(dto)
except Exception as e:
    print("Error:")
    print(e)
