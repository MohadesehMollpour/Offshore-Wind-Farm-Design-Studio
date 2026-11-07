"""C10: Weibull distribution and alternatives."""
from backend.engine import analyze
CATEGORY_ID = 'C10'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
