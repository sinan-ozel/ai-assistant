"""Verify that a tool missing @tool.mcp(title=...) crashes the MCP server.

The test agent mounts a single cortex tool (bad_tool__untitled_tool) that has
no @tool.mcp decorator. The expected sequence is:

  1. mcp_server.py fails to import the tool (ValueError logged immediately).
  2. FastAPI retries connecting to localhost:8001 for ~15 s then calls os._exit(1).
  3. backend_exit_listener catches the fastapi exit and kills the container.

The test confirms that (a) the specific error is present in the captured
stdout/stderr log and (b) the health endpoint is unreachable after the crash.
"""

import os
import time
from pathlib import Path

import requests

BASE_URL = os.getenv("BASE_URL", "http://app:8000")
LOG_FILE = Path("/logs/app.log")

# The MCP server exits very quickly, but FastAPI spends ~15 s retrying the
# connection before giving up.  30 s is enough to cover both phases.
_CRASH_WAIT_SECONDS = 30


def test_missing_title_logs_error_and_crashes():
    """App with a title-less MCP tool must log the error and go down."""
    # Phase 1 — error is logged almost immediately (mcp_server import fails
    # within the first second).  Wait briefly so the log is flushed.
    time.sleep(5)

    assert LOG_FILE.exists(), (
        f"Log file not found at {LOG_FILE}. "
        "Check that the logs volume is mounted in both app and tests services."
    )

    log = LOG_FILE.read_text()

    assert "a title is required" in log, (
        "Expected 'a title is required' in app logs.\n"
        f"Log tail:\n{log[-1500:]}"
    )
    assert "bad_tool__untitled_tool" in log, (
        "Expected the offending tool name 'bad_tool__untitled_tool' in app logs.\n"
        f"Log tail:\n{log[-1500:]}"
    )
    assert "@tool.mcp(title='...')" in log, (
        "Expected decorator hint '@tool.mcp(title=...)' in app logs.\n"
        f"Log tail:\n{log[-1500:]}"
    )

    # Phase 2 — wait for the full crash cycle (FastAPI retry loop + shutdown).
    time.sleep(_CRASH_WAIT_SECONDS)

    # Phase 3 — the server must be down.
    is_healthy = False
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=3)
        is_healthy = r.status_code == 200
    except requests.exceptions.ConnectionError:
        pass  # expected: container has exited

    assert not is_healthy, (
        "App should not be healthy after loading a tool with no title. "
        "Check that the crash propagation chain (mcp_server → fastapi → "
        "backend_exit_listener) is working correctly."
    )
