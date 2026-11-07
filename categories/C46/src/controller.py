"""C46: Shared helicopters, vessels, ports and spares."""
from backend.engine import analyze
CATEGORY_ID = 'C46'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
