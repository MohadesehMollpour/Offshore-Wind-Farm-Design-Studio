"""C39: Oil/gas field and depleted reservoir discovery."""
from backend.engine import analyze
CATEGORY_ID = 'C39'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
