from backend.catalog import BY_ID
def test_c34_contract():
    c=BY_ID['C34']
    assert len(c["charts"]) == 2
    assert c["inputs"]
