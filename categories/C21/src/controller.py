"""C21: Power curve, cut-in, cut-out and rated output."""
from backend.engine import analyze
CATEGORY_ID = 'C21'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
