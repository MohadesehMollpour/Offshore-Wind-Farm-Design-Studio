"""C22: Support structures and fatigue."""
from backend.engine import analyze
CATEGORY_ID = 'C22'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
