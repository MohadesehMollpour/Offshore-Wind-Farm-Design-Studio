from backend.catalog import BY_ID
def test_c36_contract():
    c=BY_ID['C36']
    assert len(c["charts"]) == 2
    assert c["inputs"]
