"""Streamlit chat application for agent interaction."""

import uuid

import requests
import streamlit as st

# Configuration
API_BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{API_BASE_URL}/v1/agent/chat"


def initialize_session_state():
    """Initialize session state variables."""
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
    if "user_id" not in st.session_state:
        st.session_state.user_id = "streamlit-user"
    if "messages" not in st.session_state:
        st.session_state.messages = []


def send_message(message: str) -> dict:
    """Send a message to the agent chat endpoint."""
    payload = {
        "message": message,
        "conversation_id": st.session_state.conversation_id,
        "user_id": st.session_state.user_id,
        "stream": False,
    }

    try:
        response = requests.post(CHAT_ENDPOINT, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with agent: {str(e)}")
        return None


def reset_conversation():
    """Start a new conversation."""
    st.session_state.conversation_id = str(uuid.uuid4())
    st.session_state.messages = []


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Agent Chat",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    initialize_session_state()

    # Sidebar for chat
    with st.sidebar:
        st.title("💬 Agent Chat")

        # Conversation controls
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(
                f"Conversation ID: {st.session_state.conversation_id[:8]}..."
            )
        with col2:
            if st.button("🔄", help="New conversation"):
                reset_conversation()
                st.rerun()

        st.divider()

        # Chat messages display
        chat_container = st.container(height=500)
        with chat_container:
            for msg in st.session_state.messages:
                role = msg["role"]
                content = msg["content"]

                if role == "user":
                    st.chat_message("user").write(content)
                else:
                    st.chat_message("assistant").write(content)

        # Chat input at bottom of sidebar
        user_input = st.chat_input("Type your message here...")

        if user_input:
            # Add user message to history
            st.session_state.messages.append(
                {"role": "user", "content": user_input}
            )

            # Send to agent and get response
            with st.spinner("Thinking..."):
                response = send_message(user_input)

            if response:
                # Add assistant response to history
                st.session_state.messages.append(
                    {"role": "assistant", "content": response["message"]}
                )

            # Rerun to update chat display
            st.rerun()

    # Main content area (mostly empty as requested)
    st.title("Agent Chat Interface")
    st.markdown("### Welcome to the Agent Chat")
    st.markdown("""
    Use the sidebar on the left to chat with the agent. The conversation is stateful,
    so the agent will remember your previous messages within the same conversation.

    **Features:**
    - 💬 Persistent conversation memory
    - 🔄 Start new conversations anytime
    - 📝 Full chat history
    """)

    # Display some stats if there are messages
    if st.session_state.messages:
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Messages", len(st.session_state.messages))
        with col2:
            user_msgs = sum(
                1 for m in st.session_state.messages if m["role"] == "user"
            )
            st.metric("Your Messages", user_msgs)
        with col3:
            assistant_msgs = sum(
                1 for m in st.session_state.messages if m["role"] == "assistant"
            )
            st.metric("Agent Responses", assistant_msgs)


if __name__ == "__main__":
    main()
