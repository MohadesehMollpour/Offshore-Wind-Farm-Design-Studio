from backend.catalog import BY_ID
def test_c64_contract():
    c=BY_ID['C64']
    assert len(c["charts"]) == 2
    assert c["inputs"]
