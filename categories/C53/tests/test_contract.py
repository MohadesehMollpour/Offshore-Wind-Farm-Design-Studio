from backend.catalog import BY_ID
def test_c53_contract():
    c=BY_ID['C53']
    assert len(c["charts"]) == 2
    assert c["inputs"]
