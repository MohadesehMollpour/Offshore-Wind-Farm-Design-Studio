from backend.catalog import BY_ID
def test_c31_contract():
    c=BY_ID['C31']
    assert len(c["charts"]) == 2
    assert c["inputs"]
