"""Pytest fixtures for agent_with_eval tests."""

import os

import pytest
import redis


def _make_client():
    redis_host = os.getenv("REDIS_HOST", "redis-test")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    return redis.Redis(host=redis_host, port=redis_port, decode_responses=False)


def _clear_eval_keys(client):
    keys = client.keys("memory:*agent_eval*")
    if keys:
        client.delete(*keys)


@pytest.fixture(scope="session", autouse=True)
def clear_eval_state_once():
    """Clear evaluation state keys once at the start of the session."""
    _clear_eval_keys(_make_client())
    yield


@pytest.fixture
def clear_eval_state():
    """Clear evaluation state keys before this specific test (setup only)."""
    _clear_eval_keys(_make_client())
