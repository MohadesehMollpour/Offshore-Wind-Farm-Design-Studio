"""C17: Sediment geology and geohazards."""
from backend.engine import analyze
CATEGORY_ID = 'C17'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
