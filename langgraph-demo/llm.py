from langchain.tools import tool
from langchain.chat_models import init_chat_model


model = init_chat_model(
    "qwen3:1.7b",
    model_provider="ollama",
    temperature=0.1,
    reasoning=False,
    top_p=0.9,
)


# Define tools
@tool
def multiply(a: int, b: int) -> int:
    """Multiply `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Adds `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """Divide `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a / b


@tool 
def subtract(a: int, b: int) -> int:
    """Subtract `b` from `a`.

    Args:
        a: First int
        b: Second int
    """
    return a - b


# Augment the LLM with tools
tools = [add, multiply, divide, subtract]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)

from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
import operator


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int


from langchain.messages import SystemMessage
from datetime import datetime

QWEN3_0_6B_SYSTEM_PROMPT = """
You are a helpful assistant tasked with performing arithmetic on a set of inputs.
When given a complex problem, decompose it into smaller steps and use the available tools to compute the final answer.
First you make a plan on how to solve the problem step by step like this:
1. Do this
2. With the result of step 1, do that
3. With the result of step 2, do another thing
After making the plan, execute it step by step.
Perform only one tool call at a time and wait for the observation before proceeding to the next step.
Then call the next tool with the result of the previous tool call as needed.
Never try to do multiple steps at once, that's not allowed.
"""

GEMMA_3_4B_SYSTEM_PROMPT = """
You are a helpful assistant tasked with performing arithmetic on a set of inputs.
When given a complex problem, decompose it into smaller steps and use the available tools to compute the final answer.
Go one step at a time, performing only one tool call at a time and waiting for the observation before proceeding to the next step.
"""

STRICT_SYSTEM_PROMPT = """
You are a calculator assistant. You must follow these rules EXACTLY:

1. You can only make ONE tool call at a time
2. After each tool call, you must wait for the result
3. Use the result from the previous tool call in your next tool call
4. Never make multiple tool calls in a single response

For the problem "First divide 10 by 2. Then to that add 3. Finally multiply the result by 10":
- Step 1: Call divide(10, 2) and wait for result
- Step 2: Call add(result_from_step1, 3) and wait for result  
- Step 3: Call multiply(result_from_step2, 10)

Only make ONE tool call per response. Wait for the result before proceeding.
"""


def llm_call(state: dict):
    """LLM decides whether to call a tool or not"""
    print(f"[{datetime.now().isoformat()}] LLM Call with messages:", state["messages"])

    return {
        "messages": [
            model_with_tools.invoke(
                [
                    SystemMessage(
                        content=STRICT_SYSTEM_PROMPT
                    )
                ]
                + state["messages"]
            )
        ],
        "llm_calls": state.get('llm_calls', 0) + 1
    }


from langchain.messages import ToolMessage


def tool_node(state: dict):
    """Performs the tool call"""

    result = []
    print(f"[{datetime.now().isoformat()}] Tool call with tool_calls:", state["messages"][-1].tool_calls)
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}


from typing import Literal
from langgraph.graph import StateGraph, START, END


def should_continue(state: MessagesState) -> Literal["tool_node", END]: # type: ignore
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls: # type: ignore
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return END

# Build workflow
agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)    # type: ignore
agent_builder.add_node("tool_node", tool_node)  # type: ignore

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", END]
)
agent_builder.add_edge("tool_node", "llm_call")

# Compile the agent
agent = agent_builder.compile()

# Show the agent using matplotlib
import matplotlib.pyplot as plt
from PIL import Image as PILImage
from io import BytesIO

# Invoke
from langchain.messages import HumanMessage

messages = [HumanMessage(content="First divide 10 by 2. Then to that add 3. Finally multiply the result by 10.")] # 20/2 - ((3+4) * 10))
messages = agent.invoke({"messages": messages}) # type: ignore
for m in messages["messages"]:
    m.pretty_print()

import os
import re

jsonl_files = [f for f in os.listdir(".") if re.match(r"^\d*messages\.jsonl$", f)]
prefixes = [int(re.match(r"^(\d*)messages\.jsonl$", f).group(1) or 0) for f in jsonl_files] # type: ignore
new_prefix = max(prefixes) + 1 if prefixes else 0
new_filename = f"{new_prefix}messages.jsonl"

with open(new_filename, "w", encoding="utf-8") as f:
    for m in messages["messages"]:
        f.write(m.json() + "\n")
# Show the agent
# png_data = agent.get_graph(xray=True).draw_mermaid_png()
# image = PILImage.open(BytesIO(png_data))
# plt.imshow(image)
# plt.axis('off')
# plt.show()