from backend.catalog import BY_ID
def test_c06_contract():
    c=BY_ID['C06']
    assert len(c["charts"]) == 2
    assert c["inputs"]
