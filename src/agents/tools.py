from langchain_core.tools import tool
from src.logic.janus_client import query_pc_build_es

@tool
def get_pc_recommendations(budget: int) -> str:
    """
    Use this tool when the user asks for a PC recommendation or build.
    Input should be a single integer representing the budget in dollars.
    Returns a list of compatible parts found by the Expert System.
    """
    results = query_pc_build_es(budget)

    # Check for errors
    if isinstance(results, str):
        return results
    
    if not results:
        return "No builds found under the specified budget. Please try increasing your budget."
    
    response_lines = [f"Found {len(results)} valid PC builds:"]
    for i, build in enumerate(results, 1):
        line = f"{i}. CPU: {build['Cpu']}, Motherboard: {build['Mobo']}, Total Cost: ${build['Cost']}"
        response_lines.append(line)
    
    return "\n".join(response_lines)

@tool
def use_internal_knowledge(input_text: str) -> str:
    """
    Use this tool for general questions about PC building, hardware specs,
    or related topics that do not require querying the Expert System.
    Input should be a string containing the user's question.
    Returns instructions to the LLM to answer based on its internal knowledge.
    """
    return (
        "Please answer the following question using your internal knowledge "
        "about PC building and hardware specifications:\n\n"
        f"Question: {input_text}"
    )
