"""C29: Monthly production and hourly generation proxy."""
from backend.engine import analyze
CATEGORY_ID = 'C29'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
