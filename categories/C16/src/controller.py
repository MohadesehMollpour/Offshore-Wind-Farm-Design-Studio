"""C16: Bathymetry and seabed slope."""
from backend.engine import analyze
CATEGORY_ID = 'C16'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
