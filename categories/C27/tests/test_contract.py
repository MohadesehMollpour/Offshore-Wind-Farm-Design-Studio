from backend.catalog import BY_ID
def test_c27_contract():
    c=BY_ID['C27']
    assert len(c["charts"]) == 2
    assert c["inputs"]
