"""C19: Scour, seabed mobility and cable burial."""
from backend.engine import analyze
CATEGORY_ID = 'C19'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
