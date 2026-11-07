from backend.catalog import BY_ID
def test_c10_contract():
    c=BY_ID['C10']
    assert len(c["charts"]) == 2
    assert c["inputs"]
