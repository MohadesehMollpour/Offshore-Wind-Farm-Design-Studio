"""C37: Existing, consented and planned wind farms."""
from backend.engine import analyze
CATEGORY_ID = 'C37'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
