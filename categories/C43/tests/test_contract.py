from backend.catalog import BY_ID
def test_c43_contract():
    c=BY_ID['C43']
    assert len(c["charts"]) == 2
    assert c["inputs"]
