from __future__ import annotations

import os
from typing import List

import httpx

from ..mock_data import MOCK_STATS
from ..schemas import StatRecord
from ..themes import THEMES

ESTAT_ENDPOINT = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"

class EstatClient:
    def __init__(self, app_id: str | None = None) -> None:
        self.app_id = app_id or os.getenv("ESTAT_APP_ID")

    async def fetch(self, theme: str, pref: str | None = None, years: int = 20) -> List[StatRecord]:
        theme_def = THEMES.get(theme)
        if not theme_def:
            raise ValueError(f"unsupported theme: {theme}")

        if not self.app_id or not theme_def.stats_data_id:
            return self._last_n_years(self._mock(theme, pref), years)

        params = {
            "appId": self.app_id,
            "statsDataId": theme_def.stats_data_id,
            "metaGetFlg": "Y",
            "cntGetFlg": "N",
            "explanationGetFlg": "N",
            "annotationGetFlg": "N",
            "sectionHeaderFlg": "1",
            "replaceSpChars": "0",
            "lang": "J",
        }
        if theme_def.cd_cat01:
            params["cdCat01"] = theme_def.cd_cat01

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(ESTAT_ENDPOINT, params=params)
            resp.raise_for_status()
            data = resp.json()

        values = data.get("GET_STATS_DATA", {}).get("STATISTICAL_DATA", {}).get("DATA_INF", {}).get("VALUE", [])
        if isinstance(values, dict):
            values = [values]

        records: List[StatRecord] = []
        for row in values:
            pref_code = str(row.get("@area", ""))
            pref_name = "全国" if pref_code == "" else row.get("@area_name", "不明")
            if pref and pref != pref_code:
                continue
            try:
                value = float(str(row.get("$", "0")).replace(",", ""))
            except ValueError:
                continue
            year_raw = row.get("@time", "2025")
            year = int(str(year_raw)[:4]) if str(year_raw)[:4].isdigit() else 2025
            # Keep yearly rows only to avoid mixing monthly/quarterly points in line chart.
            if len(str(year_raw)) >= 6 and str(year_raw)[4:6] not in {"00", "--"}:
                continue
            records.append(
                StatRecord(
                    source="e-Stat",
                    theme=theme,
                    label=theme_def.indicator_label,
                    prefecture_code=pref_code or "00",
                    prefecture_name=pref_name,
                    value=value,
                    unit=theme_def.unit,
                    year=year,
                )
            )

        if not records:
            return self._last_n_years(self._mock(theme, pref), years)

        return self._last_n_years(self._pick_single_series(records, pref), years)

    def _mock(self, theme: str, pref: str | None = None) -> List[StatRecord]:
        target_pref = pref or "00"
        rows = [m for m in MOCK_STATS if m.theme == theme and m.prefecture_code == target_pref]
        return [
            StatRecord(
                source="mock",
                theme=r.theme,
                label=r.label,
                prefecture_code=r.prefecture_code,
                prefecture_name=r.prefecture_name,
                value=r.value,
                unit=r.unit,
                year=r.year,
            )
            for r in rows
        ]

    def _pick_single_series(self, records: List[StatRecord], pref: str | None) -> List[StatRecord]:
        if pref:
            filtered = [r for r in records if r.prefecture_code == pref]
            return filtered

        national = [r for r in records if r.prefecture_code in {"", "00"}]
        if national:
            return national

        by_year: dict[int, StatRecord] = {}
        for rec in records:
            if rec.year not in by_year:
                by_year[rec.year] = rec.model_copy()
                by_year[rec.year].prefecture_code = "00"
                by_year[rec.year].prefecture_name = "全国"
            else:
                by_year[rec.year].value += rec.value
        return list(by_year.values())

    def _last_n_years(self, records: List[StatRecord], years: int) -> List[StatRecord]:
        if not records:
            return []
        sorted_rows = sorted(records, key=lambda r: r.year)
        by_year: dict[int, StatRecord] = {}
        for row in sorted_rows:
            by_year[row.year] = row
        deduped = [by_year[y] for y in sorted(by_year.keys())]
        return deduped[-years:]
