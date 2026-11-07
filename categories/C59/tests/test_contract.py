from backend.catalog import BY_ID
def test_c59_contract():
    c=BY_ID['C59']
    assert len(c["charts"]) == 2
    assert c["inputs"]
