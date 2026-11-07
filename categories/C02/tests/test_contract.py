from backend.catalog import BY_ID
def test_c02_contract():
    c=BY_ID['C02']
    assert len(c["charts"]) == 2
    assert c["inputs"]
