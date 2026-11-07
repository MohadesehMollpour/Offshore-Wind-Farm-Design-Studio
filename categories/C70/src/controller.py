"""C70: Investor report and technical annexes."""
from backend.engine import analyze
CATEGORY_ID = 'C70'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
