from backend.catalog import BY_ID
def test_c54_contract():
    c=BY_ID['C54']
    assert len(c["charts"]) == 2
    assert c["inputs"]
