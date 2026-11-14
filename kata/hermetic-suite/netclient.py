"""Minimal network client that silently falls back on socket errors."""

import socket


def fetch_config(host: str = "config.example.invalid", port: int = 443) -> str:
    """Resolve and connect to a remote config host; return 'default' on failure."""
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        family, socktype, proto, _, sockaddr = infos[0]
        with socket.socket(family, socktype, proto) as sock:
            sock.settimeout(0.2)
            sock.connect(sockaddr)
        return "remote"
    except OSError:
        return "default"


def probe_metadata(timeout: float = 0.2) -> bool:
    """Mimic SDK metadata probes that tolerate unreachable link-local hosts."""
    for host, port in (("metadata.google.internal", 80), ("169.254.169.254", 80)):
        try:
            infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
            family, socktype, proto, _, sockaddr = infos[0]
            with socket.socket(family, socktype, proto) as sock:
                sock.settimeout(timeout)
                sock.connect(sockaddr)
            return True
        except OSError:
            continue
    return False


def connect_literal(ip: str, port: int = 443) -> bool:
    """Connect directly to an IP literal, bypassing socket.getaddrinfo."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            sock.connect((ip, port))
        return True
    except OSError:
        return False


def resolve_loopback(port: int = 8000) -> str:
    """Resolve local loopback address for an in-process test server."""
    infos = socket.getaddrinfo("127.0.0.1", port, type=socket.SOCK_STREAM)
    return infos[0][4][0]
