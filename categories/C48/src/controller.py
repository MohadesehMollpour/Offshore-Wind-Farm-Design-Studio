"""C48: Protected areas, habitats and ecology baselines."""
from backend.engine import analyze
CATEGORY_ID = 'C48'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
