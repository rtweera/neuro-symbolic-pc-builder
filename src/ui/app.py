# Path fixes to allow imports from project root
# --------------------------------
import sys
import pathlib

# Ensure project root is on sys.path so `import src...` works when Chainlit loads this module
project_root = pathlib.Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# --------------------------------

import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage

from src.agents.agent import agent

# CONSTANTS
CHAT_HISTORY_KEY = "chat_history"

@cl.on_chat_start
def start_chat():
    """
    Initialize the chat session by setting up an empty chat history.
    """
    cl.user_session.set(CHAT_HISTORY_KEY, [])
    print("--- Chat session started ---")

@cl.on_message
async def handle_user_message(user_message: cl.Message):
    """
    Handle incoming chat messages.

    Args:
        user_message (cl.Message): The message sent by the user.

    Returns:
        None
    """
    print(f"Received user message: {user_message}")

    chat_history = cl.user_session.get(CHAT_HISTORY_KEY, [])
    if chat_history is None:
        raise ValueError("Chat history is not initialized.")
    chat_history.append(HumanMessage(content=user_message.content))

    # Prepare inputs for the agent & final response variable
    inputs = {"messages": chat_history}
    ui_final_response = cl.Message(content="")

    # Stream the agent's thought process and responses
    for event in agent.stream(inputs, stream_mode="values"):    # type: ignore
        latest_agent_message = event["messages"][-1]

        # Detect Tool Calls
        # If tool call, display it in the UI as a step
        if hasattr(latest_agent_message, "tool_calls") and latest_agent_message.tool_calls:
            for tool_call in latest_agent_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                # Collapsible step for tool call
                async with cl.Step(f"Tool Call: {tool_name}", type="tool") as step:
                    step.input = f"Tool: {tool_name}"
                    step.output = f"Arguments: {tool_args}"
                    step.language = "json"

                
        # Detect AI Messages
        elif latest_agent_message.type == "ai" and latest_agent_message.content:
            # Update the final response in the UI
            ui_final_response.content = latest_agent_message.content
    
    # send to user
    await ui_final_response.send()

    # Update chat history
    chat_history.append(AIMessage(content=ui_final_response.content))
    cl.user_session.set(CHAT_HISTORY_KEY, chat_history)