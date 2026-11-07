"""C26: Gross annual energy calculation."""
from backend.engine import analyze
CATEGORY_ID = 'C26'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
