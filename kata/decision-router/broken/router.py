from dataclasses import dataclass

FALLBACK = "llm"  # the normal, general-purpose answer path


@dataclass(frozen=True)
class Decision:
    route: str
    confidence: float


def route(client, utterance: str) -> Decision:
    scores = client.decide(utterance)
    best = max(scores, key=scores.get)   # argmax: the model's "best" route, however weak
    return Decision(route=best, confidence=scores[best])
