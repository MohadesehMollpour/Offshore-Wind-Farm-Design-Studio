"""C32: Offshore substation and protection design."""
from backend.engine import analyze
CATEGORY_ID = 'C32'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
