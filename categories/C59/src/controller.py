"""C59: OPEX, insurance, tax and decommissioning."""
from backend.engine import analyze
CATEGORY_ID = 'C59'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
