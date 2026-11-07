"""C50: Cumulative impact and mitigation plan."""
from backend.engine import analyze
CATEGORY_ID = 'C50'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
