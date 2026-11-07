from backend.catalog import BY_ID
def test_c04_contract():
    c=BY_ID['C04']
    assert len(c["charts"]) == 2
    assert c["inputs"]
