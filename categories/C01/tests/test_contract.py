from backend.catalog import BY_ID
def test_c01_contract():
    c=BY_ID['C01']
    assert len(c["charts"]) == 2
    assert c["inputs"]
