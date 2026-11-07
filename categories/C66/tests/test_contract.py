from backend.catalog import BY_ID
def test_c66_contract():
    c=BY_ID['C66']
    assert len(c["charts"]) == 2
    assert c["inputs"]
