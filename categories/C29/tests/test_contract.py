from backend.catalog import BY_ID
def test_c29_contract():
    c=BY_ID['C29']
    assert len(c["charts"]) == 2
    assert c["inputs"]
