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
class GameData:
    jackpot: float | None
    is_roll_down: bool | None = None

    def is_high_prized(self, prize_threshold: float) -> bool:
        if self.is_roll_down:
            return True
        return self.jackpot is not None and self.jackpot >= prize_threshold


class BaseGame(ABC):
    name: str
    emoji: str
    url: str
    draw_days: list[Weekday]
    prize_threshold: float  # pounds

    _headers: dict = {"User-Agent": "Mozilla/5.0 (compatible; NationalLotteryNotifier/1.0)"}

    def fetch_draw_data(self) -> GameData:
        try:
            response = requests.get(self.url, headers=self._headers, timeout=10)
            response.raise_for_status()
            return self.parse(response.text)
        except Exception as e:
            print(f"[{self.name}] fetch failed: {e}")
            return GameData(jackpot=None)

    @abstractmethod
    def parse(self, xml_text: str) -> GameData: ...
