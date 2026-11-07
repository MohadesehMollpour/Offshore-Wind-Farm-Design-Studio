"""C62: Construction/operations HSE and emergency response."""
from backend.engine import analyze
CATEGORY_ID = 'C62'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
