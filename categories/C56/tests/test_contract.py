from backend.catalog import BY_ID
def test_c56_contract():
    c=BY_ID['C56']
    assert len(c["charts"]) == 2
    assert c["inputs"]
