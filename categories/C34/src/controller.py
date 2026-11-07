"""C34: Candidate grid substations and connection status."""
from backend.engine import analyze
CATEGORY_ID = 'C34'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
