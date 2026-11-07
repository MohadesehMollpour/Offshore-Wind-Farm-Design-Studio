from backend.catalog import BY_ID
def test_c05_contract():
    c=BY_ID['C05']
    assert len(c["charts"]) == 2
    assert c["inputs"]
