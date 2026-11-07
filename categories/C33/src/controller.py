"""C33: Export route and onshore landfall."""
from backend.engine import analyze
CATEGORY_ID = 'C33'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
