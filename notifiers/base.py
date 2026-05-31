from abc import ABC, abstractmethod


class BaseNotifier(ABC):
    @abstractmethod
    def send(self, results: list[tuple[str, float, float]]) -> None:
        """Send notification for qualifying games.

        results: list of (game_name, jackpot_pounds, threshold_pounds)
        """
