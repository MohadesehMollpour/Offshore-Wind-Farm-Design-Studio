"""C65: Life cycle, consents and critical path."""
from backend.engine import analyze
CATEGORY_ID = 'C65'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
