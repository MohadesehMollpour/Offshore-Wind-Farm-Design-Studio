"""C07: Historical wind speed at several hub heights."""
from backend.engine import analyze
CATEGORY_ID = 'C07'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
