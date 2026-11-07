"""C66: Repowering, reuse and decommissioning."""
from backend.engine import analyze
CATEGORY_ID = 'C66'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
