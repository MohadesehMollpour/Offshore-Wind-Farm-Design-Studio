"""C13: Wave conditions and vessel weather windows."""
from backend.engine import analyze
CATEGORY_ID = 'C13'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
