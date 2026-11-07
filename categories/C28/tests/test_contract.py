from backend.catalog import BY_ID
def test_c28_contract():
    c=BY_ID['C28']
    assert len(c["charts"]) == 2
    assert c["inputs"]
