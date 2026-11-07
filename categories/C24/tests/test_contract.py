from backend.catalog import BY_ID
def test_c24_contract():
    c=BY_ID['C24']
    assert len(c["charts"]) == 2
    assert c["inputs"]
