"""C18: Geotechnical survey and foundations feasibility."""
from backend.engine import analyze
CATEGORY_ID = 'C18'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
