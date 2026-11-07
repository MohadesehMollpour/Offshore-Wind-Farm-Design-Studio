from backend.catalog import BY_ID
def test_c63_contract():
    c=BY_ID['C63']
    assert len(c["charts"]) == 2
    assert c["inputs"]
