"""C27: Losses and net energy calculation."""
from backend.engine import analyze
CATEGORY_ID = 'C27'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
