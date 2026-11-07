from backend.catalog import BY_ID
def test_c39_contract():
    c=BY_ID['C39']
    assert len(c["charts"]) == 2
    assert c["inputs"]
