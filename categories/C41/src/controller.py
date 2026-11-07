"""C41: Carbon licence, ownership and permitted rights."""
from backend.engine import analyze
CATEGORY_ID = 'C41'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
