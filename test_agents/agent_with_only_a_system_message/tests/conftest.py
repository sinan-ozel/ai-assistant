"""Pytest fixtures for agent_with_only_a_system_message tests."""

import os
import socket

import pytest
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis-test")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))


@pytest.fixture
def clear_test_memory():
    """Clear test conversation keys in Redis before and after each test."""
    try:
        with socket.create_connection((REDIS_HOST, REDIS_PORT), timeout=2):
            redis_reachable = True
    except OSError:
        redis_reachable = False

    if not redis_reachable:
        yield
        return

    client = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, decode_responses=False
    )

    def _clear():
        keys = client.keys("memory:test-son-*")
        if keys:
            client.delete(*keys)

    _clear()
    yield
    _clear()


@pytest.fixture(scope="session")
def clear_multi_tenancy_memory():
    """Clear multi-tenancy test keys once at the start of the session.

    Session-scoped so that state persists between the chained tests in
    test_multi_tenancy.py but the slate is clean at the start of each run.
    """
    client = None
    try:
        with socket.create_connection((REDIS_HOST, REDIS_PORT), timeout=2):
            client = redis.Redis(
                host=REDIS_HOST, port=REDIS_PORT, decode_responses=False
            )
            keys = client.keys("memory:test-mt-*")
            if keys:
                client.delete(*keys)
    except OSError:
        pass

    yield

    if client is not None:
        keys = client.keys("memory:test-mt-*")
        if keys:
            client.delete(*keys)
