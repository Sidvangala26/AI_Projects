import os
from typing import Annotated, TypedDict, List, Dict, Any, Optional
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from IPython.display import Image, display
import asyncio
import gradio as gr
import uuid
from dotenv import load_dotenv
from llm_tools import tool_email
from models import State

load_dotenv(override=True)

graph_builder = StateGraph(State)

# Ensure main thread has an event loop (required for create_async_playwright_browser on Python 3.10+)
asyncio.set_event_loop(asyncio.new_event_loop())
async_browser = create_async_playwright_browser(headless=False)
toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
tools = toolkit.get_tools()
tool_dict = {tool.name: tool for tool in tools}

navigate_tool = tool_dict.get("navigate_browser")
extract_text_tool = tool_dict.get("extract_text")

def chatbot_latest(state:State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

async def run_browser_demo():
    await navigate_tool.arun({"url": "https://www.cnn.com"})
    return await extract_text_tool.arun({})

async def chat(user_input: str, history):
    result = await graph.ainvoke({"messages": [{"role": "user", "content": user_input}]}, config=config)
    return result["messages"][-1].content

if navigate_tool and extract_text_tool:
    # text = asyncio.get_event_loop().run_until_complete(run_browser_demo())
    all_tools = tools + [tool_email]
    print(all_tools)


    # Playwright llm logic
    llm = ChatOpenAI(model="gpt-4o-mini")
    llm_with_tools = llm.bind_tools(all_tools)

    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot_latest)
    graph_builder.add_node("tools", ToolNode(tools=all_tools))
    graph_builder.add_conditional_edges( "chatbot", tools_condition, "tools")
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")

    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)


    config = {"configurable": {"thread_id": "10"}}

    gr.ChatInterface(chat).launch()



# Basic Demo Graph
# graph_builder.add_node("first_node", our_first_node)
# graph_builder.add_edge(START, "first_node")
# graph_builder.add_edge("first_node", END)
# demo_graph = graph_builder.compile()

# LLM Graph
# graph_builder.add_node("chatbot", chatbot_node)
# graph_builder.add_edge(START, "chatbot")
# graph_builder.add_edge("chatbot", END)
# demo_graph = graph_builder.compile()

# def chat(user_input: str, history):
#     state = State(messages=[{"role": "user", "content": user_input}])
#     result = demo_graph.invoke(state)
#     print(result)
#     return result["messages"][-1].content
# gr.ChatInterface(chat).launch()

# Un comment to see picture view of graph
# png_bytes = demo_graph.get_graph().draw_mermaid_png()
# with open("graph.png", "wb") as f:
#     f.write(png_bytes)
# os.startfile("graph.png")