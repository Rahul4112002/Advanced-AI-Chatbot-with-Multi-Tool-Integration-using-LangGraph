# backend.py

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
except ImportError:
    # Fallback for deployment environments
    from langgraph.checkpoint.memory import MemorySaver as SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv
import sqlite3
import requests
import os
import streamlit as st

# Load environment variables (works locally)
load_dotenv()

# Function to get API key from environment or Streamlit secrets
def get_api_key(key_name):
    # Try environment variable first
    api_key = os.getenv(key_name)
    if api_key:
        return api_key
    
    # Try Streamlit secrets (for cloud deployment)
    try:
        return st.secrets[key_name]
    except:
        return None

# -------------------
# 1. LLM
# -------------------
# Get GROQ API key from environment or Streamlit secrets
groq_api_key = get_api_key("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables or Streamlit secrets")

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=groq_api_key
)

# -------------------
# 2. Tools
# -------------------
# Tools
search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}




@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
    r = requests.get(url)
    return r.json()



tools = [search_tool, get_stock_price, calculator]
llm_with_tools = llm.bind_tools(tools)

# -------------------
# 3. State
# -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# -------------------
# 4. Nodes
# -------------------
def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

# -------------------
# 5. Checkpointer
# -------------------
# Use memory-based checkpointer for cloud deployment reliability
try:
    # Try SQLite first for local development
    import tempfile
    import os

    # Create database in a writable location
    if "HOME" in os.environ or "STREAMLIT_SHARING" in os.environ:
        # Cloud environment - use memory saver for reliability
        from langgraph.checkpoint.memory import MemorySaver
        checkpointer = MemorySaver()
    else:
        # Local environment - use SQLite
        db_path = "chatbot.db"
        conn = sqlite3.connect(database=db_path, check_same_thread=False)
        checkpointer = SqliteSaver(conn=conn)
except Exception as e:
    # Fallback to memory saver
    from langgraph.checkpoint.memory import MemorySaver
    checkpointer = MemorySaver()

# -------------------
# 6. Graph
# -------------------
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")

graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge('tools', 'chat_node')

chatbot = graph.compile(checkpointer=checkpointer)

# -------------------
# 7. Helper
# -------------------
def retrieve_all_threads():
    try:
        all_threads = set()
        for checkpoint in checkpointer.list(None):
            all_threads.add(checkpoint.config["configurable"]["thread_id"])
        return list(all_threads)
    except Exception as e:
        # Return empty list if unable to retrieve threads
        return []
