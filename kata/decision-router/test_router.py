from decisions import FakeDecisions
from router import FALLBACK, route


def test_router_acts_when_sure_and_abstains_when_not():
    client = FakeDecisions()

    sure = route(client, "how did my agents do this week?")
    assert sure.route == "snapshot"

    unsure = route(client, "write me a poem about rain")
    assert unsure.route == FALLBACK, f"routed a poem to {unsure.route!r} at confidence {unsure.confidence:.2f}"
