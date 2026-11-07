from backend.catalog import BY_ID
def test_c13_contract():
    c=BY_ID['C13']
    assert len(c["charts"]) == 2
    assert c["inputs"]
