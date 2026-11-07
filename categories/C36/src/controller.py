"""C36: Grid reinforcement costs/timeline uncertainty."""
from backend.engine import analyze
CATEGORY_ID = 'C36'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
