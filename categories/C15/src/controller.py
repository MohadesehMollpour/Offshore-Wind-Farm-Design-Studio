"""C15: Climate change and storm scenarios."""
from backend.engine import analyze
CATEGORY_ID = 'C15'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
