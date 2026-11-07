from backend.catalog import BY_ID
def test_c12_contract():
    c=BY_ID['C12']
    assert len(c["charts"]) == 2
    assert c["inputs"]
