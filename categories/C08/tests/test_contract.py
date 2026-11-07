from backend.catalog import BY_ID
def test_c08_contract():
    c=BY_ID['C08']
    assert len(c["charts"]) == 2
    assert c["inputs"]
