"""C04: Distance to coast, ports and substations."""
from backend.engine import analyze
CATEGORY_ID = 'C04'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
