"""C42: CO2 transport infrastructure and emission sources."""
from backend.engine import analyze
CATEGORY_ID = 'C42'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
