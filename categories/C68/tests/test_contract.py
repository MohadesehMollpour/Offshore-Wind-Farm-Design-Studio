from backend.catalog import BY_ID
def test_c68_contract():
    c=BY_ID['C68']
    assert len(c["charts"]) == 2
    assert c["inputs"]
