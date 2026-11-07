from backend.catalog import BY_ID
def test_c70_contract():
    c=BY_ID['C70']
    assert len(c["charts"]) == 2
    assert c["inputs"]
