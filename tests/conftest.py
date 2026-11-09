import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture(autouse=True)
def fake_edge(monkeypatch):
    """Replace the network call with a short tone whose pitch depends on the
    voice, and record every call."""
    from audiogen import engines
    calls = []

    def fake(text, voice, rate=1.0, pitch_hz=0, target_dbfs=-20.0):
        calls.append({"text": text, "voice": voice, "rate": rate})
        f = 200 + (sum(map(ord, voice)) % 300)
        t = np.arange(int(24000 * 0.3)) / 24000
        return (0.3 * np.sin(2 * np.pi * f * t)).astype(np.float32), 24000

    monkeypatch.setattr(engines, "synth_voice", fake)
    monkeypatch.setattr(engines, "unavailable_reason", lambda: "")
    return calls
