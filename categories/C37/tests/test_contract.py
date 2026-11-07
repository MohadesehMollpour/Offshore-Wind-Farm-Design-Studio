from backend.catalog import BY_ID
def test_c37_contract():
    c=BY_ID['C37']
    assert len(c["charts"]) == 2
    assert c["inputs"]
