from ai.validator import parse_and_validate


def test_parse_and_validate_normalizes_nested_list_items():
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

    dto = parse_and_validate(test_json)

    assert dto.crime_type == "theft"
    assert dto.vehicles == ["make: Bajaj Pulsar Ns, n_number: TS09AB4587"]
    assert dto.stolen_items == [
        "item: Riding helmet, value: 5000",
        "item: Personal documents, value: None",
    ]
