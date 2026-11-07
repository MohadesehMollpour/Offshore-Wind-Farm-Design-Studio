from backend.catalog import BY_ID
def test_c32_contract():
    c=BY_ID['C32']
    assert len(c["charts"]) == 2
    assert c["inputs"]
