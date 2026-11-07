"""C51: Emissions, materials and lifecycle carbon."""
from backend.engine import analyze
CATEGORY_ID = 'C51'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
