# tests/test_electricity_log.py
import datetime as dt

from src.api.electricity_log import log_raw_prices


def test_log_raw_prices_serializes_json(caplog):
    caplog.set_level("INFO")

    date = dt.date(2023, 1, 1)
    data = {"foo": "bar"}

    log_raw_prices("test_source", date, data)

    messages = [rec.getMessage() for rec in caplog.records]
    assert any("raw_prices source=test_source" in m for m in messages)
    assert any("foo" in m for m in messages)


def test_log_raw_prices_handles_unserializable_and_truncates(caplog):
    caplog.set_level("INFO")

    class Unserializable:
        # json.dumps(Unserializable()) → TypeError → except-haara
        pass

    date = dt.date(2023, 1, 1)
    # rakennetaan pitkä data, jotta truncation-haara varmasti laukeaa
    long_string = "x" * 3000
    data = {"val": long_string, "u": Unserializable()}

    log_raw_prices("test_source", date, data)

    messages = [rec.getMessage() for rec in caplog.records]
    # pitäisi olla logirivi
    assert any("raw_prices source=test_source" in m for m in messages)

    joined = "\n".join(messages)
    # truncation-merkintä
    assert "... (truncated)" in joined
    # ja pituus selvästi alle alkuperäisen 3000 merkin
    assert len(joined) < 2500
