"""C58: CAPEX and financing assumptions."""
from backend.engine import analyze
CATEGORY_ID = 'C58'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
