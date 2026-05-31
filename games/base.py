from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
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
            return self.parse(response.text)
        except Exception as e:
            print(f"[{self.name}] fetch failed: {e}")
            return DrawData(jackpot=None, rollover_count=None)

    @abstractmethod
    def parse(self, xml_text: str) -> DrawData: ...
