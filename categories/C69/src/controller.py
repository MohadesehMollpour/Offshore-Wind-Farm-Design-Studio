"""C69: Management dashboard and interactive geospatial layers."""
from backend.engine import analyze
CATEGORY_ID = 'C69'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
