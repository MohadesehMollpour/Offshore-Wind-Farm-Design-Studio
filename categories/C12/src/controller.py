"""C12: Turbulence and extreme wind design."""
from backend.engine import analyze
CATEGORY_ID = 'C12'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
