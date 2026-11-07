"""C01: Candidate AOI polygon and coordinates."""
from backend.engine import analyze
CATEGORY_ID = 'C01'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
