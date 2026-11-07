"""C25: Multiple-objective optimisation."""
from backend.engine import analyze
CATEGORY_ID = 'C25'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
