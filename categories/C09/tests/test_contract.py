from backend.catalog import BY_ID
def test_c09_contract():
    c=BY_ID['C09']
    assert len(c["charts"]) == 2
    assert c["inputs"]
