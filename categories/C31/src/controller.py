"""C31: Inter-array cables and string topology."""
from backend.engine import analyze
CATEGORY_ID = 'C31'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
