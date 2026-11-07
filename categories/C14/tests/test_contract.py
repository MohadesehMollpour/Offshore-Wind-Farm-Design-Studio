from backend.catalog import BY_ID
def test_c14_contract():
    c=BY_ID['C14']
    assert len(c["charts"]) == 2
    assert c["inputs"]
