import streamlit as st
from step3_tool_chatbot_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid
import os

# Page configuration
st.set_page_config(
    page_title="LangGraph AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================== Utilities ===========================
def generate_thread_id():
    return uuid.uuid4()

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)
    st.session_state["message_history"] = []

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def load_conversation(thread_id):
    try:
        state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
        # Check if messages key exists in state values, return empty list if not
        return state.values.get("messages", [])
    except Exception as e:
        st.error(f"Error loading conversation: {e}")
        return []

# ======================= Session Initialization ===================
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    try:
        st.session_state["chat_threads"] = retrieve_all_threads()
    except Exception as e:
        st.session_state["chat_threads"] = []
        st.warning("Starting with fresh chat threads due to database initialization.")

add_thread(st.session_state["thread_id"])

# ============================ Sidebar ============================
st.sidebar.title("🤖 LangGraph Chatbot")
st.sidebar.markdown("---")

# Info section
with st.sidebar.expander("ℹ️ About", expanded=False):
    st.markdown("""
    **Features:**
    - 🔍 Web Search (DuckDuckGo)
    - 📈 Stock Prices (Alpha Vantage)
    - 🧮 Calculator
    - 💾 Persistent Conversations
    - ⚡ Real-time Streaming
    """)

if st.sidebar.button("🆕 New Chat", use_container_width=True):
    reset_chat()
    st.rerun()

st.sidebar.markdown("### 💬 My Conversations")

# Show recent conversations
for i, thread_id in enumerate(st.session_state["chat_threads"][::-1][:10]):  # Show last 10
    thread_str = str(thread_id)
    display_name = f"Chat {len(st.session_state['chat_threads']) - i}"
    
    if st.sidebar.button(
        display_name, 
        key=f"thread_{thread_str}",
        use_container_width=True,
        help=f"Thread ID: {thread_str[:8]}..."
    ):
        st.session_state["thread_id"] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            temp_messages.append({"role": role, "content": msg.content})
        st.session_state["message_history"] = temp_messages
        st.rerun()

# ============================ Main UI ============================
st.title("🤖 AI Chatbot with LangGraph")
st.markdown("Ask me anything! I can search the web, get stock prices, and perform calculations.")

# Check for API key
if not os.getenv("GROQ_API_KEY") and not st.secrets.get("GROQ_API_KEY"):
    st.error("⚠️ GROQ_API_KEY not found! Please add it to your Streamlit secrets.")
    st.stop()

# Display current thread info
col1, col2 = st.columns([3, 1])
with col2:
    current_thread = str(st.session_state["thread_id"])
    st.caption(f"💭 Thread: {current_thread[:8]}...")

# Render history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type your message here...")

if user_input:
    # Show user's message
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {"thread_id": st.session_state["thread_id"]},
        "run_name": "chat_turn",
    }

    # Assistant streaming block
    with st.chat_message("assistant"):
        # Use a mutable holder so the generator can set/modify it
        status_holder = {"box": None}

        def ai_only_stream():
            try:
                for message_chunk, metadata in chatbot.stream(
                    {"messages": [HumanMessage(content=user_input)]},
                    config=CONFIG,
                    stream_mode="messages",
                ):
                    # Lazily create & update the SAME status container when any tool runs
                    if isinstance(message_chunk, ToolMessage):
                        tool_name = getattr(message_chunk, "name", "tool")
                        if status_holder["box"] is None:
                            status_holder["box"] = st.status(
                                f"🔧 Using `{tool_name}` …", expanded=True
                            )
                        else:
                            status_holder["box"].update(
                                label=f"🔧 Using `{tool_name}` …",
                                state="running",
                                expanded=True,
                            )

                    # Stream ONLY assistant tokens
                    if isinstance(message_chunk, AIMessage):
                        yield message_chunk.content
            except Exception as e:
                st.error(f"Error: {e}")
                yield "I apologize, but I encountered an error. Please try again."

        ai_message = st.write_stream(ai_only_stream())

        # Finalize only if a tool was actually used
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished", state="complete", expanded=False
            )

    # Save assistant message
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
        Built with ❤️ using LangGraph, Groq, and Streamlit | 
        <a href='https://github.com/your-repo' target='_blank'>View Source</a>
    </div>
    """, 
    unsafe_allow_html=True
)