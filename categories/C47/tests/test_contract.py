from backend.catalog import BY_ID
def test_c47_contract():
    c=BY_ID['C47']
    assert len(c["charts"]) == 2
    assert c["inputs"]
