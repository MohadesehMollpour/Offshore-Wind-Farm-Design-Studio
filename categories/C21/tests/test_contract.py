from backend.catalog import BY_ID
def test_c21_contract():
    c=BY_ID['C21']
    assert len(c["charts"]) == 2
    assert c["inputs"]
