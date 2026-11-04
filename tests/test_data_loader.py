"""Tests using synthetic station data (no public data dependency)."""
import math

import pandas as pd

from src.data_loader import clean_gira_data


def _samples():
    return pd.DataFrame({
        "desigcomercial": ["1 - Estação A", "2 - Estação B", "3 - Estação C"],
        "numbicicletas": [3, 0, 12],
        "numdocas": [6, 0, 5],
        "entity_ts": ["2023-01-01T10:00:00Z"] * 3,
        "estado": ["ok"] * 3,
        "position": ["[-9.14, 38.72]", "[-9.15, 38.73]", "malformed"],
    })


def test_invalid_capacity_is_missing_not_zero():
    out = clean_gira_data(_samples())
    assert out.iloc[0]["occupancy_rate"] == 0.5
    assert math.isnan(out.iloc[1]["occupancy_rate"])
    assert math.isnan(out.iloc[2]["occupancy_rate"])


def test_invalid_coordinates_are_missing_not_fatal():
    out = clean_gira_data(_samples())
    assert out.iloc[0]["lon"] == -9.14
    assert out.iloc[0]["lat"] == 38.72
    assert math.isnan(out.iloc[2]["lon"])
    assert math.isnan(out.iloc[2]["lat"])
