"""Hermetic network guard blocking non-local DNS and socket connects."""

from __future__ import annotations

import errno
import ipaddress
import socket
import threading
from dataclasses import dataclass, field

# Probes cloud SDKs issue on startup when running off-cloud; fail fast offline
# without marking the test itself as a hermeticity violation.
OFFLINE_EXPECTED = frozenset({"metadata.google.internal", "169.254.169.254"})

_AF_UNIX = getattr(socket, "AF_UNIX", -1)


def is_local(host: object) -> bool:
    """Return True if host is localhost or a loopback IP."""
    if not isinstance(host, str) or not host:
        return False
    clean = host.strip("[]").split("%", 1)[0].lower()
    if clean == "localhost":
        return True
    try:
        return ipaddress.ip_address(clean).is_loopback
    except ValueError:
        return False


@dataclass
class Ledger:
    """Thread-safe record of blocked outbound attempts attributed by owner."""

    owner: str = "<collection>"
    entries: list[tuple[str, str, str]] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def record(self, host: str, op: str) -> None:
        with self._lock:
            self.entries.append((self.owner, host, op))

    def set_owner(self, owner: str) -> None:
        with self._lock:
            self.owner = owner

    def pop_for(self, owner: str) -> list[tuple[str, str]]:
        with self._lock:
            matched = [(h, op) for o, h, op in self.entries if o == owner]
            self.entries = [e for e in self.entries if e[0] != owner]
            return matched

    def pop_foreign(self) -> list[tuple[str, str, str]]:
        with self._lock:
            out = list(self.entries)
            self.entries.clear()
            return out


_LEDGER = Ledger()
_INSTALLED = False


def install() -> None:
    """Patch socket.getaddrinfo and socket.socket.connect/connect_ex once."""
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    orig_getaddrinfo = socket.getaddrinfo
    orig_connect = socket.socket.connect
    orig_connect_ex = socket.socket.connect_ex

    def guarded_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        if host is not None and not is_local(host):
            key = str(host).strip("[]").split("%", 1)[0].lower()
            if key not in OFFLINE_EXPECTED:
                _LEDGER.record(str(host), "getaddrinfo")
            raise socket.gaierror(
                socket.EAI_NONAME,
                f"hermetic test: network lookup to {host!r} blocked",
            )
        return orig_getaddrinfo(host, port, family, type, proto, flags)

    def _blocked_peer(sock, address) -> str | None:
        if sock.family == _AF_UNIX:
            return None
        if isinstance(address, tuple) and address:
            host = address[0]
            if not is_local(host):
                return str(host)
        return None

    def guarded_connect(self, address):
        peer = _blocked_peer(self, address)
        if peer is not None:
            if peer.lower() not in OFFLINE_EXPECTED:
                _LEDGER.record(peer, "connect")
            raise OSError(
                errno.ENETUNREACH,
                f"hermetic test: connect to {peer!r} blocked",
            )
        return orig_connect(self, address)

    def guarded_connect_ex(self, address):
        peer = _blocked_peer(self, address)
        if peer is not None:
            if peer.lower() not in OFFLINE_EXPECTED:
                _LEDGER.record(peer, "connect_ex")
            return errno.ENETUNREACH
        return orig_connect_ex(self, address)

    socket.getaddrinfo = guarded_getaddrinfo
    socket.socket.connect = guarded_connect
    socket.socket.connect_ex = guarded_connect_ex


def begin_owner(owner: str) -> None:
    _LEDGER.set_owner(owner)


def end_owner(owner: str) -> None:
    _LEDGER.set_owner(f"<after {owner}>")


def pop_violations(owner: str) -> list[tuple[str, str]]:
    return _LEDGER.pop_for(owner)


def pop_non_test_violations() -> list[tuple[str, str, str]]:
    return _LEDGER.pop_foreign()
