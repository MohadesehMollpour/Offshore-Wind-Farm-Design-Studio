from backend.catalog import BY_ID
def test_c40_contract():
    c=BY_ID['C40']
    assert len(c["charts"]) == 2
    assert c["inputs"]
