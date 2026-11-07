"""C40: CO2 storage reservoir suitability screening."""
from backend.engine import analyze
CATEGORY_ID = 'C40'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
