"""C03: Site suitability and multi-criteria comparison."""
from backend.engine import analyze
CATEGORY_ID = 'C03'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
