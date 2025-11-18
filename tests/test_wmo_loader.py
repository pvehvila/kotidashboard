# tests/test_wmo_map_loader.py
import pandas as pd

import src.api.wmo_map_loader as l


def test_scalar_extracts_right_values():
    # scalar from Series
    s = pd.Series([10])
    assert l._scalar(s) == 10

    # scalar from numpy-like item()
    class Fake:
        def item(self):
            return 42

    assert l._scalar(Fake()) == 42

    # raw value
    assert l._scalar(5) == 5


def test_normalize_cell_strips_and_removes_none():
    assert l._normalize_cell(None) == ""
    assert l._normalize_cell(float("nan")) == ""
    assert l._normalize_cell(" x ") == "x"


def test_build_wmo_maps_basic():
    df = pd.DataFrame(
        {
            "wmo": [1, 2],
            "day": ["d100", "d200"],
            "night": ["n100", "n200"],
        }
    )
    out = l.build_wmo_foreca_maps(df, "wmo", "day", "night")
    assert out["day"] == {1: "d100", 2: "d200"}
    assert out["night"] == {1: "n100", 2: "n200"}


def test_build_wmo_maps_last_full_fallback():
    df = pd.DataFrame(
        {
            "wmo": [1, 2],
            "day": ["d100", ""],  # second row inherits
            "night": ["", "n200"],  # first inherits nothing
        }
    )
    out = l.build_wmo_foreca_maps(df, "wmo", "day", "night")
    assert out["day"] == {1: "d100", 2: "d100"}
    assert out["night"] == {2: "n200"}  # first row night empty → skipped


def test_build_wmo_maps_invalid_wmo_rows_are_skipped():
    df = pd.DataFrame(
        {
            "wmo": ["x", 2],
            "day": ["d100", "d200"],
            "night": ["n100", "n200"],
        }
    )
    out = l.build_wmo_foreca_maps(df, "wmo", "day", "night")
    assert out["day"] == {2: "d200"}
    assert out["night"] == {2: "n200"}


def test_read_raw_wmo_mapping_returns_empty_if_no_files(tmp_path, monkeypatch):
    # pakotetaan hakupolut osoittamaan tyhjään hakemistoon
    monkeypatch.setattr(l, "DATA", tmp_path)
    # override entire candidate list to pure nonexistent paths
    monkeypatch.setattr(l.Path, "exists", lambda self: False)

    df = l.read_raw_wmo_mapping()
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_load_wmo_foreca_map_uses_provided_df_and_not_file(monkeypatch):
    # varmistetaan että read_raw_wmo_mapping EI KUTSUTA
    def fail_read():
        raise AssertionError("Should not read file when df provided")

    monkeypatch.setattr(l, "read_raw_wmo_mapping", fail_read)

    df = pd.DataFrame({"wmo": [1], "day": ["d123"], "night": ["n123"]})
    out = l.load_wmo_foreca_map(df)
    assert out["day"] == {1: "d123"}
    assert out["night"] == {1: "n123"}
