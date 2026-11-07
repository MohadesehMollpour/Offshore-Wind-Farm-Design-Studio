"""C38: Cumulative wake and seabird impacts."""
from backend.engine import analyze
CATEGORY_ID = 'C38'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
