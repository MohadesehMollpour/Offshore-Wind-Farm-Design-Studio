from backend.catalog import BY_ID
def test_c15_contract():
    c=BY_ID['C15']
    assert len(c["charts"]) == 2
    assert c["inputs"]
