from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from src.agents.tools import get_pc_recommendations, use_internal_knowledge
from src.agents.config import config

# CONSTANTS
# ==============================
OLLAMA_MODEL = "llama3.1:latest"
TEMPERATURE = config[OLLAMA_MODEL]["temperature"]
SYSTEM_PROMPT = config[OLLAMA_MODEL]["system_prompt"]
# ==============================

llm = ChatOllama(model=OLLAMA_MODEL, temperature=TEMPERATURE)
tools = [get_pc_recommendations, use_internal_knowledge]
agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)

def chat_with_agent(user_input: str):
    """
    Interact with the PC building agent.
    Input: User's message as a string.
    """
    print("\n--- New Interaction ---\n", end="")
    print(f"\nUser: {user_input}")
    print("\nAgent is thinking...")
    inputs = {"messages": [HumanMessage(content=user_input)]}

    try:
        # stream_mode="values" streams only the text output at each step
        for event in agent.stream(inputs, stream_mode="values"):    # type: ignore
            last_message = event["messages"][-1]

            if last_message.type == "ai" and last_message.content:
                print(f"\nAgent: {last_message.content}")

            elif hasattr(last_message, "tool_calls") and last_message.tool_calls:
                for tool_call in last_message.tool_calls:
                    print(f"\n[Tool Call] {tool_call['name']} with input: {tool_call['args']}")

    except Exception as e:
        print(f"❌ Error during agent interaction: {e}")
    finally:
        print("\n--- End of Interaction ---\n")

if __name__ == "__main__":
    # Example interaction
    chat_with_agent("Can you recommend a PC build for under $700?")

    # General Chat (Pure SLM)
    chat_with_agent("What is the difference between DDR4 and DDR5 RAM?")