"""C35: Transmission boundaries and constraint risk."""
from backend.engine import analyze
CATEGORY_ID = 'C35'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
