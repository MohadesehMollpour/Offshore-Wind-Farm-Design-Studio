"""C56: Operations port, CTV/SOV and crew access."""
from backend.engine import analyze
CATEGORY_ID = 'C56'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
