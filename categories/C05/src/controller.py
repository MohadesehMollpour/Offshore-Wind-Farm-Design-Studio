"""C05: Navigation, shipping and aviation constraints."""
from backend.engine import analyze
CATEGORY_ID = 'C05'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
