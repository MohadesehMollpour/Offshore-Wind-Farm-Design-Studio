"""C09: Wind seasonal, diurnal, extreme behaviour."""
from backend.engine import analyze
CATEGORY_ID = 'C09'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
