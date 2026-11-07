from backend.catalog import BY_ID
def test_c20_contract():
    c=BY_ID['C20']
    assert len(c["charts"]) == 2
    assert c["inputs"]
