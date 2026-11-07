"""C11: Vertical shear and stability."""
from backend.engine import analyze
CATEGORY_ID = 'C11'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
