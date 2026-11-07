from backend.catalog import BY_ID
def test_c61_contract():
    c=BY_ID['C61']
    assert len(c["charts"]) == 2
    assert c["inputs"]
