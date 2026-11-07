from backend.catalog import BY_ID
def test_c33_contract():
    c=BY_ID['C33']
    assert len(c["charts"]) == 2
    assert c["inputs"]
