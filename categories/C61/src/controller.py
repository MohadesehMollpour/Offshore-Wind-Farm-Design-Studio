"""C61: Price, discount, wake and schedule sensitivity."""
from backend.engine import analyze
CATEGORY_ID = 'C61'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
