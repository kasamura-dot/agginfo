from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeDefinition:
    key: str
    label: str
    stats_data_id: str | None
    cd_cat01: str | None
    indicator_label: str
    unit: str


THEMES: dict[str, ThemeDefinition] = {
    "population": ThemeDefinition(
        key="population",
        label="人口",
        stats_data_id="0003448235",
        cd_cat01="A1101",
        indicator_label="総人口",
        unit="人",
    ),
    "employment": ThemeDefinition(
        key="employment",
        label="雇用",
        stats_data_id="0003448243",
        cd_cat01="A1101",
        indicator_label="就業者数",
        unit="人",
    ),
    "households": ThemeDefinition(
        key="households",
        label="世帯",
        stats_data_id=None,
        cd_cat01=None,
        indicator_label="一般世帯数",
        unit="世帯",
    ),
    "cpi": ThemeDefinition(
        key="cpi",
        label="消費者物価",
        stats_data_id=None,
        cd_cat01=None,
        indicator_label="消費者物価指数",
        unit="指数",
    ),
    "tourism": ThemeDefinition(
        key="tourism",
        label="観光",
        stats_data_id=None,
        cd_cat01=None,
        indicator_label="延べ宿泊者数",
        unit="人泊",
    ),
    "wage": ThemeDefinition(
        key="wage",
        label="賃金",
        stats_data_id=None,
        cd_cat01=None,
        indicator_label="現金給与総額",
        unit="円",
    ),
}

