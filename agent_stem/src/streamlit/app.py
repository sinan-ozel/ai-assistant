"""Streamlit chat application for agent interaction."""

import base64
import json
import time
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


def send_message(message: str, media: list | None = None):
    """Send a message to the agent chat endpoint and stream the response."""
    payload = {
        "message": message,
        "conversation_id": st.session_state.conversation_id,
        "user_id": st.session_state.user_id,
        "stream": True,
        "stream_format": "sse",
    }
    if media:
        payload["media"] = media

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


def _api_ready() -> bool:
    """Return True if the agent API is up and accepting requests."""
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=1)
        return r.status_code == 200
    except Exception:
        return False


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Agent Chat",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        header [data-testid="stToolbar"] {display: none;}
        .stDeployButton {display: none;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    initialize_session_state()

    if not _api_ready():
        st.title("Agent Chat")
        with st.spinner("Agent is starting up…"):
            time.sleep(2)
        st.rerun()
        return

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

        # Image uploader — sits above the chat input
        _MIME = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp",
        }
        uploaded_files = st.file_uploader(
            "Attach images (JPEG, PNG, GIF, WebP)",
            type=list(_MIME),
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        # Chat input at bottom of sidebar
        user_input = st.chat_input("Type your message here...")

        if user_input:
            # Build media list from any uploaded images
            media = []
            for f in uploaded_files or []:
                ext = f.name.rsplit(".", 1)[-1].lower()
                mime = _MIME.get(ext, f"image/{ext}")
                b64 = base64.b64encode(f.read()).decode("utf-8")
                media.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"},
                    }
                )

            # Add user message to history
            st.session_state.messages.append(
                {"role": "user", "content": user_input}
            )

            # Send to agent and get streaming response.
            # st.write_stream does not update incrementally when called inside
            # a container that was already rendered, so we drive the generator
            # manually and update an st.empty() placeholder on each chunk.
            with chat_container:
                with st.chat_message("assistant"):
                    placeholder = st.empty()
                    response_text = ""
                    for chunk in send_message(user_input, media=media or None):
                        response_text += chunk
                        placeholder.markdown(response_text + "▌")
                    placeholder.markdown(response_text)

            if response_text:
                # Add assistant response to history
                st.session_state.messages.append(
                    {"role": "assistant", "content": response_text}
                )

            # Rerun to update chat display
            st.rerun()

    # Main content area
    st.title("Private Interface")
    st.link_button("📄 API Docs (Swagger)", f"{API_BASE_URL}/docs")

    # Library Section
    st.divider()
    st.markdown("## 📚 Library")
    st.markdown("Books indexed by the document pipeline.")

    try:
        books_response = requests.get(
            f"{API_BASE_URL}/private/v1/books", timeout=5
        )
        if books_response.status_code == 200:
            books = books_response.json()
            if not books:
                st.info(
                    "No books indexed yet. Add PDFs or Markdown files to `cortex/library/`."
                )
            else:
                # Group by shelf (first path component before '/')
                shelves: dict = {}
                for book in books:
                    parts = book["file_path"].split("/", 1)
                    if len(parts) == 2:
                        shelf, remainder = parts
                    else:
                        shelf, remainder = None, parts[0]
                    display_name = remainder.rsplit(".", 1)[0]
                    shelves.setdefault(shelf, []).append(
                        {**book, "display_name": display_name}
                    )

                def _render_book(b: dict):
                    col_name, col_chunks = st.columns([5, 1])
                    col_name.markdown(f"📖 {b['display_name']}")
                    col_chunks.caption(f"{b['chunk_count']} chunks")

                if len(shelves) <= 1:
                    # Single shelf or all at root — flat list
                    shelf_name, shelf_books = next(iter(shelves.items()))
                    if shelf_name:
                        st.markdown(f"**{shelf_name}**")
                    for b in shelf_books:
                        _render_book(b)
                else:
                    # Multiple shelves — hierarchical expanders
                    for shelf_name in sorted(
                        shelves, key=lambda s: ("" if s is None else s)
                    ):
                        shelf_books = shelves[shelf_name]
                        label = shelf_name if shelf_name else "(root)"
                        with st.expander(
                            f"📂 {label} — {len(shelf_books)} book(s)",
                            expanded=True,
                        ):
                            for b in shelf_books:
                                _render_book(b)
        elif books_response.status_code == 503:
            st.warning(
                "Vector store unavailable: "
                + books_response.json().get("detail", "")
            )
        else:
            st.warning(f"Could not fetch books: {books_response.status_code}")
    except Exception as e:
        st.warning(f"Could not reach books API: {e}")

    # External Tools Section
    st.divider()
    st.markdown("## 🔧 External Tools")
    st.markdown("MCP tool servers registered by this agent.")

    try:
        from redis_memory import Memory

        with Memory() as _mem:
            _mcp_tools = _mem.mcp_tools if hasattr(_mem, "mcp_tools") else []
        if not isinstance(_mcp_tools, list) or not _mcp_tools:
            st.info(
                "No external tools registered. "
                "Add a `McpServer(...)` call to `cortex/chat/prompt.py` to enable tools."
            )
        else:
            for _server in _mcp_tools:
                _url = _server.get("server_url", "unknown")
                _tools = _server.get("tools", [])
                st.markdown(f"**🌐 {_url}** — {len(_tools)} tool(s)")
                for _tool in _tools:
                    _name = _tool.get("name", "")
                    _desc = _tool.get("description", "")
                    _ro = _tool.get("read_only", False)
                    _badge = "🟢 read-only" if _ro else "🔴 write"
                    _annotation_icons = [
                        ("read_only", "👁️", "Read-only: does not modify state"),
                        (
                            "destructive",
                            "💥",
                            "Destructive: may delete or overwrite data",
                        ),
                        (
                            "idempotent",
                            "🔁",
                            "Idempotent: safe to retry with the same arguments",
                        ),
                        (
                            "open_world",
                            "🌐",
                            "Open world: interacts with external systems",
                        ),
                    ]
                    _label_icons = " ".join(
                        icon
                        for key, icon, _ in _annotation_icons
                        if _tool.get(key, False)
                    )
                    _label = f"`{_name}` {_badge}"
                    if _label_icons:
                        _label += f"  {_label_icons}"
                    with st.expander(_label, expanded=False):
                        _tooltip_icons = [
                            f'<span title="{tip}">{icon}</span>'
                            for key, icon, tip in _annotation_icons
                            if _tool.get(key, False)
                        ]
                        if _tooltip_icons:
                            st.markdown(
                                " ".join(_tooltip_icons), unsafe_allow_html=True
                            )
                        if _desc:
                            st.caption(_desc)
    except Exception as _e:
        st.info(f"External tools unavailable: {_e}")

    # Agent Evaluation DSL Section
    st.divider()
    st.markdown("## 🧪 Agent Evaluation")
    st.markdown(
        "Run the `cortex/chat/eval.py` evaluation suite against this agent."
    )

    EVAL_URL = f"{API_BASE_URL}/private/v1/agent/evaluate"

    col_run, col_cancel, col_spacer = st.columns([1, 1, 4])

    with col_run:
        if st.button("▶️ Run Evaluation", key="agent_eval_run"):
            try:
                r = requests.post(EVAL_URL, json={}, timeout=10)
                if r.status_code == 202:
                    st.success("Evaluation started!")
                elif r.status_code == 409:
                    st.warning("A run is already in progress.")
                elif r.status_code == 404:
                    st.error(
                        "No `cortex/chat/eval.py` found. "
                        "Create the file to enable evaluation."
                    )
                else:
                    st.error(f"Unexpected response: {r.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")

    # Fetch current state
    try:
        eval_resp = requests.get(EVAL_URL, timeout=5)
    except Exception as e:
        st.warning(f"Could not reach evaluation API: {e}")
        eval_resp = None

    if eval_resp is not None:
        if eval_resp.status_code == 404:
            st.info("No completed evaluation run yet.")

        elif eval_resp.status_code == 202:
            # Running
            data = eval_resp.json()
            with col_cancel:
                if st.button("❌ Cancel", key="agent_eval_cancel"):
                    try:
                        cr = requests.delete(EVAL_URL, timeout=5)
                        if cr.status_code == 200:
                            st.warning("Cancellation requested.")
                            st.rerun()
                        else:
                            st.error(f"Could not cancel: {cr.status_code}")
                    except Exception as e:
                        st.error(f"Error: {e}")

            st.info(
                f"🟡 **Running** — "
                f"case {data.get('completed_cases', 0) + 1} of "
                f"{data.get('total_cases', '?')} "
                f"(`{data.get('current_case') or 'starting…'}`)"
            )
            if data.get("started_at"):
                from datetime import datetime

                try:
                    ts = datetime.fromisoformat(data["started_at"])
                    st.caption(f"Started: {ts.strftime('%Y-%m-%d %H:%M:%S')}")
                except Exception:
                    st.caption(f"Started: {data['started_at']}")

            time.sleep(3)
            st.rerun()

        elif eval_resp.status_code == 200:
            # Completed — show results
            data = eval_resp.json()

            from datetime import datetime

            def _fmt_ts(iso: str) -> str:
                try:
                    dt = datetime.fromisoformat(iso)
                    return dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    return iso

            # Header row: suite name + timestamps
            suite_name = data.get("suite") or "Evaluation suite"
            started = data.get("started_at")
            completed = data.get("completed_at")

            st.markdown(f"### {suite_name}")

            ts_parts = []
            if started:
                ts_parts.append(f"**Run:** {_fmt_ts(started)}")
            if completed:
                ts_parts.append(f"**Completed:** {_fmt_ts(completed)}")
            if started and completed:
                try:
                    dur = (
                        datetime.fromisoformat(completed)
                        - datetime.fromisoformat(started)
                    ).total_seconds()
                    ts_parts.append(f"**Duration:** {dur:.1f}s")
                except Exception:
                    pass
            if ts_parts:
                st.caption("   ·   ".join(ts_parts))

            # Summary metrics
            total = data.get("total", 0)
            passed = data.get("passed", 0)
            failed = data.get("failed", 0)
            m1, m2, m3 = st.columns(3)
            m1.metric("Total cases", total)
            m2.metric("Passed", passed, delta=None)
            m3.metric("Failed", failed, delta=None)

            # Per-case results
            cases = data.get("cases", [])
            if cases:
                st.markdown("#### Cases")
                for case in cases:
                    case_id = case.get("id", "?")
                    passing_runs = case.get("passing_runs", 0)
                    threshold = case.get("threshold", 1)
                    total_runs = len(case.get("runs", []))
                    status = case.get("status", "fail")
                    icon = "✅" if status == "pass" else "❌"

                    with st.expander(
                        f"{icon} **{case_id}**   "
                        f"({passing_runs}/{total_runs} runs passed, "
                        f"threshold {threshold})",
                        expanded=(status == "fail"),
                    ):
                        for run in case.get("runs", []):
                            run_num = run.get("run", "?")
                            checks = run.get("checks", [])
                            run_passed = all(
                                c.get("passed", False) for c in checks
                            )
                            run_icon = "✅" if run_passed else "❌"
                            st.markdown(f"**{run_icon} Run {run_num}**")
                            for chk in checks:
                                chk_passed = chk.get("passed", False)
                                chk_icon = "✓" if chk_passed else "✗"
                                chk_type = chk.get("type", "?")
                                detail = ""
                                if chk_type == "regexp":
                                    detail = f"`{chk.get('pattern', '')}`"
                                elif chk_type == "judge":
                                    detail = (
                                        f"judge: _{chk.get('prompt', '')[:60]}_"
                                    )
                                elif chk_type == "similar_to":
                                    sim = chk.get("similarity")
                                    thr = chk.get("threshold")
                                    detail = (
                                        f"similarity {sim:.3f} "
                                        f"(threshold {thr})"
                                        if sim is not None
                                        else ""
                                    )
                                elif chk_type == "callable":
                                    detail = "callable"
                                line = f"  {chk_icon} {chk_type}"
                                if detail:
                                    line += f" — {detail}"
                                if not chk_passed and chk.get("reason"):
                                    line += f"\n  > {chk['reason']}"
                                st.markdown(line)

        else:
            st.warning(
                f"Unexpected status from evaluation API: {eval_resp.status_code}"
            )

    # Workflows Section
    st.divider()
    st.markdown("## 🔄 Workflows")
    st.markdown("Browse workflows and trigger evaluations where available.")

    # Fetch available workflows
    try:
        workflows_response = requests.get(
            f"{API_BASE_URL}/private/v1/workflows", timeout=5
        )
        if workflows_response.status_code == 200:
            workflows_data = workflows_response.json()
            all_workflows = workflows_data.get("workflows", [])

            if all_workflows:
                if not any(w.get("has_evaluation") for w in all_workflows):
                    st.caption(
                        "None of these workflows have evaluations defined. "
                        "Add an `evaluation:` section to a workflow YAML to enable testing."
                    )
                for workflow in all_workflows:
                    with st.expander(f"📊 {workflow['name']}", expanded=False):
                        st.markdown(f"**Path:** `{workflow['path']}`")
                        if workflow.get("description"):
                            st.markdown(
                                f"**Description:** {workflow['description']}"
                            )
                        if workflow.get("provider"):
                            st.markdown(f"**Provider:** {workflow['provider']}")

                        if not workflow.get("has_evaluation"):
                            st.caption(
                                "No evaluation defined for this workflow."
                            )
                        else:
                            col1, col2 = st.columns([1, 3])

                            with col1:
                                if st.button(
                                    "▶️ Run Evaluation",
                                    key=f"eval_{workflow['path']}",
                                ):
                                    try:
                                        eval_response = requests.post(
                                            f"{API_BASE_URL}/private/evaluate{workflow['path']}",
                                            timeout=10,
                                        )
                                        if eval_response.status_code == 201:
                                            st.success("Evaluation started!")
                                        elif eval_response.status_code == 409:
                                            st.warning(
                                                "Evaluation already in progress"
                                            )
                                        else:
                                            st.error(
                                                f"Failed to start: {eval_response.status_code}"
                                            )
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")

                            with col2:
                                try:
                                    results_response = requests.get(
                                        f"{API_BASE_URL}/private/evaluate{workflow['path']}/results",
                                        timeout=5,
                                    )
                                    if results_response.status_code == 200:
                                        results_data = results_response.json()
                                        status = results_data.get(
                                            "status", "idle"
                                        )

                                        status_colors = {
                                            "idle": "⚫",
                                            "running": "🟡",
                                            "completed": "🟢",
                                            "failed": "🔴",
                                            "error": "🔴",
                                            "cancelled": "⚪",
                                        }
                                        st.markdown(
                                            f"**Status:** {status_colors.get(status, '⚪')} {status.upper()}"
                                        )

                                        if results_data.get("started_at"):
                                            from datetime import datetime

                                            try:
                                                started_at = (
                                                    datetime.fromisoformat(
                                                        results_data[
                                                            "started_at"
                                                        ]
                                                    )
                                                )
                                                st.markdown(
                                                    f"**Started:** {started_at.strftime('%Y-%m-%d %H:%M:%S')}"
                                                )
                                            except Exception:
                                                st.markdown(
                                                    f"**Started:** {results_data['started_at']}"
                                                )

                                        if (
                                            status == "completed"
                                            and results_data.get("results")
                                        ):
                                            results = results_data["results"]
                                            st.markdown("### Results")

                                            if results.get("errors"):
                                                st.error(
                                                    "⚠️ **Evaluation completed with errors:**"
                                                )
                                                for error in results["errors"]:
                                                    st.error(f"• {error}")
                                                st.markdown("---")

                                            metric_cols = st.columns(4)
                                            with metric_cols[0]:
                                                st.metric(
                                                    "Total Cases",
                                                    results.get(
                                                        "total_cases", 0
                                                    ),
                                                )
                                            with metric_cols[1]:
                                                st.metric(
                                                    "Passed",
                                                    results.get(
                                                        "passed_cases", 0
                                                    ),
                                                )
                                            with metric_cols[2]:
                                                st.metric(
                                                    "Failed",
                                                    results.get(
                                                        "failed_cases", 0
                                                    ),
                                                )
                                            with metric_cols[3]:
                                                st.metric(
                                                    "Duration",
                                                    f"{results.get('duration', 0):.1f}s",
                                                )

                                            if st.checkbox(
                                                "Show detailed results",
                                                key=f"details_{workflow['path']}",
                                            ):
                                                for case in results.get(
                                                    "cases", []
                                                ):
                                                    case_status = (
                                                        "✅"
                                                        if case.get("passed")
                                                        else "❌"
                                                    )
                                                    st.markdown(
                                                        f"**{case_status} {case.get('id')}**"
                                                    )
                                                    st.markdown(
                                                        f"Passed: {case.get('pass_count')}/{case.get('repeat')} "
                                                        f"(threshold: {case.get('threshold')})"
                                                    )
                                                    if not case.get("passed"):
                                                        for run in case.get(
                                                            "runs", []
                                                        ):
                                                            if not run.get(
                                                                "passed"
                                                            ):
                                                                for (
                                                                    step
                                                                ) in run.get(
                                                                    "steps", []
                                                                ):
                                                                    for (
                                                                        exp
                                                                    ) in step.get(
                                                                        "expectations",
                                                                        [],
                                                                    ):
                                                                        if not exp.get(
                                                                            "passed"
                                                                        ) and exp.get(
                                                                            "error"
                                                                        ):
                                                                            st.error(
                                                                                f"Run {run['run']}, step {step['step']} "
                                                                                f"({exp['type']}): {exp['error']}"
                                                                            )

                                        elif status == "error":
                                            st.error(
                                                "🚨 **Evaluation stopped due to error:**"
                                            )
                                            st.error(
                                                f"• {results_data.get('error', 'Unknown error')}"
                                            )

                                        elif status == "failed":
                                            st.warning(
                                                "⚠️ **Evaluation completed with failures:**"
                                            )
                                            st.warning(
                                                f"• {results_data.get('error', 'Some test cases failed')}"
                                            )

                                        elif status == "running":
                                            st.info("Evaluation in progress...")
                                            if st.button(
                                                "❌ Cancel Evaluation",
                                                key=f"cancel_{workflow['path']}",
                                            ):
                                                cancel_response = requests.post(
                                                    f"{API_BASE_URL}/private/cancel-evaluation{workflow['path']}",
                                                    timeout=10,
                                                )
                                                if (
                                                    cancel_response.status_code
                                                    == 200
                                                ):
                                                    st.warning(
                                                        "Cancellation requested"
                                                    )
                                                    st.rerun()
                                                else:
                                                    st.error(
                                                        f"Failed to cancel: {cancel_response.status_code}"
                                                    )
                                            time.sleep(2)
                                            st.rerun()

                                        elif status == "cancelled":
                                            st.warning(
                                                "⚪ **Evaluation was cancelled**"
                                            )
                                except Exception as e:
                                    st.warning(
                                        f"Could not fetch results: {str(e)}"
                                    )
            else:
                st.info(
                    "No workflows defined yet. "
                    "Add YAML files to `cortex/workflows/`."
                )
        else:
            st.warning("Could not fetch workflows list")
    except Exception as e:
        st.error(f"Error loading workflows: {str(e)}")


if __name__ == "__main__":
    main()
