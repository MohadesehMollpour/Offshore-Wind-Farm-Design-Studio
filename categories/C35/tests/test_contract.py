from backend.catalog import BY_ID
def test_c35_contract():
    c=BY_ID['C35']
    assert len(c["charts"]) == 2
    assert c["inputs"]
