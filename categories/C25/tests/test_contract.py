from backend.catalog import BY_ID
def test_c25_contract():
    c=BY_ID['C25']
    assert len(c["charts"]) == 2
    assert c["inputs"]
