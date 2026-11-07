"""C45: Reuse of offshore platform O&M facilities."""
from backend.engine import analyze
CATEGORY_ID = 'C45'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
