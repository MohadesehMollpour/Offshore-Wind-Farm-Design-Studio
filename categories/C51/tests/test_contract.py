from backend.catalog import BY_ID
def test_c51_contract():
    c=BY_ID['C51']
    assert len(c["charts"]) == 2
    assert c["inputs"]
