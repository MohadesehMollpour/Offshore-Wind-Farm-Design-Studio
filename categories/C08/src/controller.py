"""C08: Wind direction and sector frequency."""
from backend.engine import analyze
CATEGORY_ID = 'C08'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
