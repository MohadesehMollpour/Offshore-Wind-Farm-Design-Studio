"""C43: Storage operation, monitoring, liabilities."""
from backend.engine import analyze
CATEGORY_ID = 'C43'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
