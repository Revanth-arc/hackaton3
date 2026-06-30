def extract_strings(data):
    texts = []
    if isinstance(data, (list, tuple)):
        if len(data) == 2 and isinstance(data[0], str):
            texts.append(data[0])
        else:
            for item in data:
                texts.extend(extract_strings(item))
    return texts


def test_extract_strings_handles_nested_paddleocr_output():
    result = [[[[0, 0], [1, 0], [1, 1], [0, 1]], ("FIR TEST 123", 0.99)]]

    assert extract_strings(result) == ["FIR TEST 123"]
