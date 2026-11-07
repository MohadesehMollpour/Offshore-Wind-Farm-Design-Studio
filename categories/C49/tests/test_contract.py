from backend.catalog import BY_ID
def test_c49_contract():
    c=BY_ID['C49']
    assert len(c["charts"]) == 2
    assert c["inputs"]
