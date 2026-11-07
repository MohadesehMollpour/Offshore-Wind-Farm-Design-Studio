from backend.catalog import BY_ID
def test_c69_contract():
    c=BY_ID['C69']
    assert len(c["charts"]) == 2
    assert c["inputs"]
