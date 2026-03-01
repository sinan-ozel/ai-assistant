"""Streamlit chat application for agent interaction."""

import json
import uuid
import time

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


def send_message(message: str):
    """Send a message to the agent chat endpoint and stream the
    response."""
    payload = {
        "message": message,
        "conversation_id": st.session_state.conversation_id,
        "user_id": st.session_state.user_id,
        "stream": True,
        "stream_format": "sse",
    }

    try:
        response = requests.post(
            CHAT_ENDPOINT, json=payload, timeout=60, stream=True
        )
        response.raise_for_status()

        # Stream the response chunks
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                data = line[6:]  # Remove "data: " prefix
                if data == "[DONE]":
                    break
                else:
                    chunk = json.loads(data)
                    # Extract content from delta
                    if "delta" in chunk and "content" in chunk["delta"]:
                        yield chunk["delta"]["content"]

    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with agent: {str(e)}")
        return


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

            # Send to agent and get streaming response
            with chat_container:
                with st.chat_message("assistant"):
                    response_text = st.write_stream(send_message(user_input))

            if response_text:
                # Add assistant response to history
                st.session_state.messages.append(
                    {"role": "assistant", "content": response_text}
                )

            # Rerun to update chat display
            st.rerun()

    # Main content area
    st.title("Agent Chat Interface")
    st.markdown("### Welcome to the Agent Chat")
    st.markdown("""
    Use the sidebar on the left to chat with the agent. The \
conversation is stateful, so the agent will remember your previous \
messages within the same conversation.

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

    # Workflow Evaluations Section
    st.divider()
    st.markdown("## 🔄 Workflows")
    st.markdown("Trigger and monitor automated evaluations for workflows.")

    # Fetch available workflows
    try:
        workflows_response = requests.get(f"{API_BASE_URL}/private/v1/workflows", timeout=5)
        if workflows_response.status_code == 200:
            workflows_data = workflows_response.json()
            evaluatable_workflows = [
                w for w in workflows_data.get("workflows", [])
                if w.get("has_evaluation")
            ]

            if evaluatable_workflows:
                for workflow in evaluatable_workflows:
                    with st.expander(f"📊 {workflow['name']}", expanded=False):
                        st.markdown(f"**Path:** `{workflow['path']}`")
                        if workflow.get("description"):
                            st.markdown(f"**Description:** {workflow['description']}")
                        if workflow.get("provider"):
                            st.markdown(f"**Provider:** {workflow['provider']}")

                        col1, col2 = st.columns([1, 3])

                        with col1:
                            if st.button(f"▶️ Run Evaluation", key=f"eval_{workflow['path']}"):
                                try:
                                    eval_response = requests.post(
                                        f"{API_BASE_URL}/private/evaluate{workflow['path']}",
                                        timeout=10
                                    )
                                    if eval_response.status_code == 201:
                                        st.success("Evaluation started!")
                                        # Don't rerun here to avoid clearing the success message
                                    elif eval_response.status_code == 409:
                                        st.warning("Evaluation already in progress")
                                    else:
                                        st.error(f"Failed to start: {eval_response.status_code}")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")

                        with col2:
                            # Fetch and display current status
                            try:
                                results_response = requests.get(
                                    f"{API_BASE_URL}/private/evaluate{workflow['path']}/results",
                                    timeout=5
                                )
                                if results_response.status_code == 200:
                                    results_data = results_response.json()
                                    status = results_data.get("status", "idle")

                                    # Status indicator
                                    status_colors = {
                                        "idle": "⚫",
                                        "running": "🟡",
                                        "completed": "🟢",
                                        "failed": "🔴",
                                        "error": "🔴",
                                        "cancelled": "⚪"
                                    }
                                    st.markdown(f"**Status:** {status_colors.get(status, '⚪')} {status.upper()}")

                                    # Show started_at if available
                                    if results_data.get("started_at"):
                                        from datetime import datetime
                                        try:
                                            started_at = datetime.fromisoformat(results_data["started_at"])
                                            st.markdown(f"**Started:** {started_at.strftime('%Y-%m-%d %H:%M:%S')}")
                                        except Exception as e:
                                            # Fallback to showing raw timestamp
                                            st.markdown(f"**Started:** {results_data['started_at']}")

                                    # Show results if completed
                                    if status == "completed" and results_data.get("results"):
                                        results = results_data["results"]
                                        st.markdown("### Results")

                                        # Show errors prominently if present
                                        if results.get("errors"):
                                            st.error("⚠️ **Evaluation completed with errors:**")
                                            for error in results["errors"]:
                                                st.error(f"• {error}")
                                            st.markdown("---")

                                        metric_cols = st.columns(4)
                                        with metric_cols[0]:
                                            st.metric("Total Cases", results.get("total_cases", 0))
                                        with metric_cols[1]:
                                            st.metric("Passed", results.get("passed_cases", 0))
                                        with metric_cols[2]:
                                            st.metric("Failed", results.get("failed_cases", 0))
                                        with metric_cols[3]:
                                            st.metric("Duration", f"{results.get('duration', 0):.1f}s")

                                        # Detailed results
                                        if st.checkbox("Show detailed results", key=f"details_{workflow['path']}"):
                                            for case in results.get("cases", []):
                                                case_status = "✅" if case.get("passed") else "❌"
                                                st.markdown(f"**{case_status} {case.get('id')}**")
                                                st.markdown(
                                                    f"Passed: {case.get('pass_count')}/{case.get('repeat')} "
                                                    f"(threshold: {case.get('threshold')})"
                                                )
                                                if not case.get("passed"):
                                                    for run in case.get("runs", []):
                                                        if not run.get("passed"):
                                                            for step in run.get("steps", []):
                                                                for exp in step.get("expectations", []):
                                                                    if not exp.get("passed") and exp.get("error"):
                                                                        st.error(
                                                                            f"Run {run['run']}, step {step['step']} "
                                                                            f"({exp['type']}): {exp['error']}"
                                                                        )

                                    elif status == "error":
                                        st.error("🚨 **Evaluation stopped due to error:**")
                                        error_msg = results_data.get('error', 'Unknown error')
                                        st.error(f"• {error_msg}")

                                    elif status == "failed":
                                        st.warning("⚠️ **Evaluation completed with failures:**")
                                        error_msg = results_data.get('error', 'Some test cases failed')
                                        st.warning(f"• {error_msg}")

                                    elif status == "running":
                                        st.info("Evaluation in progress...")

                                        # Add cancel button
                                        if st.button(f"❌ Cancel Evaluation", key=f"cancel_{workflow['path']}"):
                                            cancel_response = requests.post(
                                                f"{API_BASE_URL}/private/cancel-evaluation{workflow['path']}",
                                                timeout=10
                                            )
                                            if cancel_response.status_code == 200:
                                                st.warning("Cancellation requested")
                                                st.rerun()
                                            else:
                                                st.error(f"Failed to cancel: {cancel_response.status_code}")

                                        # Poll every 2 seconds while running
                                        time.sleep(2)
                                        st.rerun()

                                    elif status == "cancelled":
                                        st.warning("⚪ **Evaluation was cancelled**")
                            except Exception as e:
                                st.warning(f"Could not fetch results: {str(e)}")
            else:
                st.info("No workflows with evaluation sections found.")
        else:
            st.warning("Could not fetch workflows list")
    except Exception as e:
        st.error(f"Error loading workflows: {str(e)}")


if __name__ == "__main__":
    main()
