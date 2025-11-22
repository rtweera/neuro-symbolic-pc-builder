import janus_swi as janus
from typing import List, Dict

# CONSTANTS
# ==============================
KB_DIR = "knowledge/"
PC_KB_FILE = "knowledge_base.pl"
PC_KB_PATH = KB_DIR + PC_KB_FILE
# ==============================


def query_pc_build_es(user_budget: int) -> List[Dict] | str:
    """
    Queries the Prolog KB for a PC build under the given budget.
    Returns a list of dictionaries: [{'Cpu': '...', 'Mobo': '...', 'Cost': ...}]
    """
    try:
        janus.consult(PC_KB_PATH)
    except Exception as e:
        return f"❌ Error loading knowledge base: {e}"
    
    query = f"recommend_build({user_budget}, Cpu, Mobo, Cost)"
    results = []
    try:
        for result in janus.query(query):
            results.append({
                'Cpu': result['Cpu'],
                'Mobo': result['Mobo'],
                'Cost': result['Cost']
            })
        return results
    except Exception as e:
        return f"❌ Error during query: {e}"