"""Direct unit checks proving the hermetic guard mechanisms under KATA=fixed."""

import errno
import os
import socket

import pytest

import netclient
from fixed import hermetic_net


def test_is_local_classifies_loopback_and_remote():
    assert hermetic_net.is_local("localhost") is True
    assert hermetic_net.is_local("127.0.0.1") is True
    assert hermetic_net.is_local("127.0.0.42") is True
    assert hermetic_net.is_local("::1") is True
    assert hermetic_net.is_local("169.254.169.254") is False
    assert hermetic_net.is_local("api.example.com") is False


@pytest.mark.skipif(
    os.environ.get("KATA", "broken") != "fixed",
    reason="guard checks require KATA=fixed",
)
def test_literal_ip_connect_blocked_and_recorded(request):
    assert netclient.connect_literal("203.0.113.10", 443) is False
    recorded = hermetic_net.pop_violations(request.node.nodeid)
    assert recorded == [("203.0.113.10", "connect")]


@pytest.mark.skipif(
    os.environ.get("KATA", "broken") != "fixed",
    reason="guard checks require KATA=fixed",
)
def test_connect_ex_returns_enetunreach(request):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        rc = sock.connect_ex(("203.0.113.11", 80))
    assert rc == errno.ENETUNREACH
    recorded = hermetic_net.pop_violations(request.node.nodeid)
    assert recorded == [("203.0.113.11", "connect_ex")]


@pytest.mark.skipif(
    os.environ.get("KATA", "broken") != "fixed",
    reason="guard checks require KATA=fixed",
)
def test_getaddrinfo_blocks_and_records_hostname(request):
    with pytest.raises(socket.gaierror, match="hermetic test"):
        socket.getaddrinfo("blocked.example.invalid", 443)
    recorded = hermetic_net.pop_violations(request.node.nodeid)
    assert recorded == [("blocked.example.invalid", "getaddrinfo")]


def test_ledger_attributes_collection_and_post_test_leaks():
    ledger = hermetic_net.Ledger()
    ledger.record("import.example.invalid", "getaddrinfo")
    ledger.set_owner("test_a")
    ledger.record("call.example.invalid", "connect")
    ledger.set_owner("<after test_a>")
    ledger.record("thread.example.invalid", "connect")

    assert ledger.pop_for("test_a") == [("call.example.invalid", "connect")]
    assert ledger.pop_foreign() == [
        ("<collection>", "import.example.invalid", "getaddrinfo"),
        ("<after test_a>", "thread.example.invalid", "connect"),
    ]

