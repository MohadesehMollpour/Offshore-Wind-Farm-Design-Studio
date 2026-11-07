from backend.catalog import BY_ID
def test_c38_contract():
    c=BY_ID['C38']
    assert len(c["charts"]) == 2
    assert c["inputs"]
