from backend.catalog import BY_ID
def test_c46_contract():
    c=BY_ID['C46']
    assert len(c["charts"]) == 2
    assert c["inputs"]
