"""C44: Offshore platform and rig inventory."""
from backend.engine import analyze
CATEGORY_ID = 'C44'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
