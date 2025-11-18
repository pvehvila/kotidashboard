# tests/test_wmo_trace.py
import src.api.wmo_trace as t


def test_trace_map_disabled_does_nothing(monkeypatch):
    t.clear_map_trace()
    monkeypatch.setattr(t, "MAP_TRACE_ENABLED", False)

    t.trace_map(1, True, 10, 5.0, 50, "d100", "reason")

    assert t.get_map_trace() == []


def test_trace_map_enabled_adds_entries(monkeypatch):
    t.clear_map_trace()
    monkeypatch.setattr(t, "MAP_TRACE_ENABLED", True)

    t.trace_map(1, True, 10, 5.0, 50, "d100", "ok")
    out = t.get_map_trace()

    assert len(out) == 1
    rec = out[0]
    assert rec["wmo"] == 1
    assert rec["key"] == "d100"
    assert rec["reason"] == "ok"


def test_trace_map_truncates_when_over_limit(monkeypatch):
    t.clear_map_trace()
    monkeypatch.setattr(t, "MAP_TRACE_ENABLED", True)

    # push 250 entries
    for i in range(250):
        t.trace_map(
            wmo=i,
            is_day=True,
            pop=None,
            temp_c=None,
            cloudcover=None,
            chosen_key=f"d{i}",
            reason="ok",
        )

    out = t.get_map_trace()

    # Oikea lopullinen koko
    assert len(out) == 169

    # viimeinen säilynyt entry
    assert out[-1]["wmo"] == 249

    # ensimmäinen säilynyt entry
    assert out[0]["wmo"] == 81
