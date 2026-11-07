"""C52: Construction port, staging and vessel choices."""
from backend.engine import analyze
CATEGORY_ID = 'C52'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
