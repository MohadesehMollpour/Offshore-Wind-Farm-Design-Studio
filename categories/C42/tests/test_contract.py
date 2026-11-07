from backend.catalog import BY_ID
def test_c42_contract():
    c=BY_ID['C42']
    assert len(c["charts"]) == 2
    assert c["inputs"]
