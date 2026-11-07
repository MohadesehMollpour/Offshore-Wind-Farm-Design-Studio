from backend.catalog import BY_ID
def test_c50_contract():
    c=BY_ID['C50']
    assert len(c["charts"]) == 2
    assert c["inputs"]
