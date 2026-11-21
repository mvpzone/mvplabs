from dataclasses import dataclass

FALLBACK = "llm"  # the normal, general-purpose answer path
THRESHOLD = 0.8   # act on the model's pick only above this


@dataclass(frozen=True)
class Decision:
    route: str
    confidence: float


def route(client, utterance: str) -> Decision:
    scores = client.decide(utterance)
    best = max(scores, key=scores.get)
    if scores[best] < THRESHOLD:
        # Abstain: keep the confidence for the record, but send the request down the normal path.
        return Decision(route=FALLBACK, confidence=scores[best])
    return Decision(route=best, confidence=scores[best])
