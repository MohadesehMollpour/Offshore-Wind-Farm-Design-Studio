"""C06: Fisheries and socioeconomic spatial conflicts."""
from backend.engine import analyze
CATEGORY_ID = 'C06'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
