"""A stand-in for a decision-model API: it scores a CLOSED set of options, it never writes text.

A real endpoint returns one probability per option for the question you ask. This fake returns numbers
shaped like that, measured from a live run, so the kata runs offline.
"""

ROUTES = {
    "snapshot": "a summary of the user's recent activity",
    "catalogue": "list what the user can run",
}

# utterance -> probability per route. Sums to 1.0: the model always has to pick *something*.
_SCORES = {
    "how did my agents do this week?": {"snapshot": 0.943, "catalogue": 0.057},
    "what investigations can I run?": {"snapshot": 0.003, "catalogue": 0.997},
    "write me a poem about rain": {"snapshot": 0.462, "catalogue": 0.538},
}


class FakeDecisions:
    def decide(self, utterance: str) -> dict[str, float]:
        return dict(_SCORES[utterance])
