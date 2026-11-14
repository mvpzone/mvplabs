"""Suite demonstrating a silent fallback masking outbound DNS/connect."""

import netclient


def test_fetch_config_degrades():
    # Software under test swallows OSError and returns 'default',
    # so this assertion passes even though a real DNS lookup fired.
    assert netclient.fetch_config("config.example.invalid") == "default"


def test_metadata_probe_degrades():
    # SDKs commonly probe cloud link-local metadata on startup.
    assert netclient.probe_metadata() is False


def test_loopback_resolves():
    # Local test servers on loopback remain allowed.
    assert netclient.resolve_loopback() == "127.0.0.1"
