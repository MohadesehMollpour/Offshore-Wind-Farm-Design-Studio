"""C23: Turbine placement and spacing."""
from backend.engine import analyze
CATEGORY_ID = 'C23'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
