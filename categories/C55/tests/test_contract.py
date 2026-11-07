from backend.catalog import BY_ID
def test_c55_contract():
    c=BY_ID['C55']
    assert len(c["charts"]) == 2
    assert c["inputs"]
