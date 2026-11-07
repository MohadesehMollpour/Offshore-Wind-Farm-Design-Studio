"""C02: Marine spatial zoning and lease rights."""
from backend.engine import analyze
CATEGORY_ID = 'C02'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
