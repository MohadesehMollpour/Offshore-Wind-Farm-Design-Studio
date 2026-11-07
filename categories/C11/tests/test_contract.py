from backend.catalog import BY_ID
def test_c11_contract():
    c=BY_ID['C11']
    assert len(c["charts"]) == 2
    assert c["inputs"]
