from backend.catalog import BY_ID
def test_c18_contract():
    c=BY_ID['C18']
    assert len(c["charts"]) == 2
    assert c["inputs"]
