from backend.catalog import BY_ID
def test_c58_contract():
    c=BY_ID['C58']
    assert len(c["charts"]) == 2
    assert c["inputs"]
