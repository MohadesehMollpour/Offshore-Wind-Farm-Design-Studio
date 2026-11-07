"""C67: Cross-agent consistency and auditability."""
from backend.engine import analyze
CATEGORY_ID = 'C67'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
