from backend.catalog import BY_ID
def test_c62_contract():
    c=BY_ID['C62']
    assert len(c["charts"]) == 2
    assert c["inputs"]
