"""C68: AI disclosure, authorship, evidence and learning."""
from backend.engine import analyze
CATEGORY_ID = 'C68'
def run(scenario, context):
    return analyze(CATEGORY_ID, scenario, context)
