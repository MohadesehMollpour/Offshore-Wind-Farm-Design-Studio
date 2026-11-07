from backend.catalog import BY_ID
def test_c30_contract():
    c=BY_ID['C30']
    assert len(c["charts"]) == 2
    assert c["inputs"]
