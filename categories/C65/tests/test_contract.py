from backend.catalog import BY_ID
def test_c65_contract():
    c=BY_ID['C65']
    assert len(c["charts"]) == 2
    assert c["inputs"]
