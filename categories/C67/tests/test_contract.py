from backend.catalog import BY_ID
def test_c67_contract():
    c=BY_ID['C67']
    assert len(c["charts"]) == 2
    assert c["inputs"]
