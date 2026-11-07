from backend.catalog import BY_ID
def test_c26_contract():
    c=BY_ID['C26']
    assert len(c["charts"]) == 2
    assert c["inputs"]
