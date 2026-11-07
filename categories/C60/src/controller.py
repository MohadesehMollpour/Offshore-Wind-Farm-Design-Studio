"""C60: LCOE, NPV, IRR and payback."""
from backend.engine import analyze
CATEGORY_ID = 'C60'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
