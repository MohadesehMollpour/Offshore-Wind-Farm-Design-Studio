"""C64: Stakeholders and community engagement."""
from backend.engine import analyze
CATEGORY_ID = 'C64'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
