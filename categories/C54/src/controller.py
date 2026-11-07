"""C54: Supply chain, lead times and procurement."""
from backend.engine import analyze
CATEGORY_ID = 'C54'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
