from backend.catalog import BY_ID
def test_c57_contract():
    c=BY_ID['C57']
    assert len(c["charts"]) == 2
    assert c["inputs"]
