from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MockStat:
    theme: str
    label: str
    prefecture_code: str
    prefecture_name: str
    value: float
    unit: str
    year: int


_PREF_NAMES = {
    "00": "全国",
    "01": "北海道",
    "13": "東京都",
    "27": "大阪府",
}

_THEME_META = {
    "population": ("総人口", "人"),
    "employment": ("就業者数", "人"),
    "households": ("一般世帯数", "世帯"),
    "cpi": ("消費者物価指数", "指数"),
    "tourism": ("延べ宿泊者数", "人泊"),
    "wage": ("現金給与総額", "円"),
}

# (base_2025, yearly_delta) for 2006-2025 synthetic series
_BASE_BY_THEME_PREF = {
    "population": {
        "00": (123400000.0, -250000.0),
        "13": (14047594.0, 25000.0),
        "27": (8772860.0, -8000.0),
        "01": (5107000.0, -35000.0),
    },
    "employment": {
        "00": (69000000.0, -90000.0),
        "13": (8300000.0, 12000.0),
        "27": (4300000.0, -5000.0),
        "01": (2600000.0, -9000.0),
    },
    "households": {
        "00": (56000000.0, 190000.0),
        "13": (7200000.0, 18000.0),
        "27": (4100000.0, 4000.0),
        "01": (2500000.0, -3000.0),
    },
    "cpi": {
        "00": (108.0, 0.6),
        "13": (108.6, 0.7),
        "27": (107.9, 0.65),
        "01": (106.8, 0.6),
    },
    "tourism": {
        "00": (610000000.0, 8500000.0),
        "13": (65000000.0, 1200000.0),
        "27": (42000000.0, 850000.0),
        "01": (39000000.0, 700000.0),
    },
    "wage": {
        "00": (340000.0, 1600.0),
        "13": (402300.0, 2400.0),
        "27": (338200.0, 1900.0),
        "01": (297500.0, 1700.0),
    },
}


def _series_value(base_2025: float, delta: float, year: int) -> float:
    value = base_2025 + delta * (year - 2025)
    return max(value, 1.0)


MOCK_STATS: list[MockStat] = []
for theme, prefs in _BASE_BY_THEME_PREF.items():
    label, unit = _THEME_META[theme]
    for pref_code, (base_2025, delta) in prefs.items():
        pref_name = _PREF_NAMES[pref_code]
        for year in range(2006, 2026):
            MOCK_STATS.append(
                MockStat(
                    theme=theme,
                    label=label,
                    prefecture_code=pref_code,
                    prefecture_name=pref_name,
                    value=round(_series_value(base_2025, delta, year), 1),
                    unit=unit,
                    year=year,
                )
            )
