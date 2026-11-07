"""C49: Birds, bats and marine mammals."""
from backend.engine import analyze
CATEGORY_ID = 'C49'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
