"""Vocabolario narrativo sostituibile, esterno al compilatore."""


def default_kinds() -> dict[str, str]:
    return {"stanza": "mondo.stanza", "cosa": "mondo.cosa"}
