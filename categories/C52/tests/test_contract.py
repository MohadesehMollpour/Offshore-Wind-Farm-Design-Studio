from backend.catalog import BY_ID
def test_c52_contract():
    c=BY_ID['C52']
    assert len(c["charts"]) == 2
    assert c["inputs"]
