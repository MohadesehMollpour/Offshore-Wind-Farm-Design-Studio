"""C20: Candidate turbine technology comparison."""
from backend.engine import analyze
CATEGORY_ID = 'C20'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
