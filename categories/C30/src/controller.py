"""C30: Energy price capture and curtailment exposure."""
from backend.engine import analyze
CATEGORY_ID = 'C30'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
