import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai.extractor import extract_fir_entities

test_text = """
On 28-06-2026, my Bajaj Pulsar Ns motorcycle (TS09AB4587) was stolen. 
Also stolen was a Riding helmet worth 5000 and Personal documents.
"""
try:
    dto = extract_fir_entities(test_text)
    print("Success:")
    print(dto)
except Exception as e:
    print("Error:")
    print(e)
