from backend.catalog import BY_ID
def test_c44_contract():
    c=BY_ID['C44']
    assert len(c["charts"]) == 2
    assert c["inputs"]
