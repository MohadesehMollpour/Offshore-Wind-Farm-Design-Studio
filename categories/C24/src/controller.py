"""C24: Wake interaction and neighbouring farm wakes."""
from backend.engine import analyze
CATEGORY_ID = 'C24'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
