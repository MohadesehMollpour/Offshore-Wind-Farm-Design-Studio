"""C63: Staffing, labour demand and skills."""
from backend.engine import analyze
CATEGORY_ID = 'C63'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
