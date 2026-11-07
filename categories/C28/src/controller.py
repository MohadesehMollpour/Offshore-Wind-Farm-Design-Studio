"""C28: P50/P75/P90 yield and uncertainty."""
from backend.engine import analyze
CATEGORY_ID = 'C28'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
