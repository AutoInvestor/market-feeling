from dataclasses import dataclass


@dataclass(frozen=True)
class RawScore:
    """
    A value object holding a single integer 0–10.
    Rounds+clamps any numeric input into that range.
    """

    value: int

    def __init__(self, raw: float):
        # round to nearest int, clamp between 0 and 10
        try:
            v = int(round(raw))
        except Exception:
            raise ValueError(f"Score must be numeric (got {raw!r})")
        v = max(0, min(10, v))
        # bypass frozen to set
        object.__setattr__(self, "value", v)
