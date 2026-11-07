from backend.catalog import BY_ID
def test_c60_contract():
    c=BY_ID['C60']
    assert len(c["charts"]) == 2
    assert c["inputs"]
