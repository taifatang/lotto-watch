from abc import ABC
from dataclasses import dataclass
from enum import IntEnum
import xml.etree.ElementTree as ET
import requests


class Weekday(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


@dataclass
class DrawData:
    jackpot: float | None
    rollover_count: int | None


class BaseGame(ABC):
    name: str
    url: str
    draw_days: list[Weekday]
    prize_threshold: float  # pounds
    max_rollovers: int | None = None

    _headers: dict = {"User-Agent": "Mozilla/5.0 (compatible; NationalLotteryNotifier/1.0)"}

    def fetch_draw_data(self) -> DrawData:
        try:
            response = requests.get(self.url, headers=self._headers, timeout=10)
            response.raise_for_status()
            return self._parse_draw_data(response.text)
        except Exception as e:
            print(f"[{self.name}] fetch failed: {e}")
            return DrawData(jackpot=None, rollover_count=None)

    def _parse_draw_data(self, xml_text: str) -> DrawData:
        try:
            root = ET.fromstring(xml_text)
            jackpot = self._parse_jackpot(root)
            rollover_count = self._parse_rollover_count(root)
            return DrawData(jackpot=jackpot, rollover_count=rollover_count)
        except Exception as e:
            print(f"[{self.name}] parse failed: {e}")
            return DrawData(jackpot=None, rollover_count=None)

    def _parse_jackpot(self, root) -> float | None:
        el = root.find(".//next-estimated-jackpot")
        if el is None or el.text is None:
            print(f"[{self.name}] <next-estimated-jackpot> not found")
            return None
        return float(el.text.replace(",", "").strip())

    def _parse_rollover_count(self, root) -> int | None:
        el = root.find(".//rollover-count")
        if el is None or el.text is None:
            return None
        return int(el.text)
