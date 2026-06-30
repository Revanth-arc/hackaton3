import requests

from ai.extractor import extract_fir_entities


def test_extract_fir_entities_uses_heuristic_fallback_when_ollama_is_unavailable(
    monkeypatch,
):
    def unavailable_ollama(*args, **kwargs):
        raise requests.exceptions.ConnectionError("Ollama is not running")

    monkeypatch.setattr("ai.extractor.requests.get", unavailable_ollama)

    test_text = """
    On 28-06-2026, my Bajaj Pulsar Ns motorcycle (TS09AB4587) was stolen.
    Also stolen was a riding helmet worth 5000 and personal documents.
    """

    dto = extract_fir_entities(test_text)

    assert dto.date == "28-06-2026"
    assert dto.crime_type == "theft"
    assert dto.vehicles == ["TS09AB4587"]
    assert dto.sections == ["BNS/IPC section review required"]
