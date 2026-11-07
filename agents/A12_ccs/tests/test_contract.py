from backend.catalog import load,BY_ID
def test_ownership_contract():
    agent=next(a for a in load('agents') if a['id']=='A12')
    assert agent['instructions'].strip()
    assert agent['categories']
    for cid in agent['categories']:
        assert agent['id'] in BY_ID[cid]['owners']
