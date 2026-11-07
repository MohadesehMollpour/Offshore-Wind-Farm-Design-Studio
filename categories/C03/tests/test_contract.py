from backend.catalog import BY_ID
def test_c03_contract():
    c=BY_ID['C03']
    assert len(c["charts"]) == 2
    assert c["inputs"]
