from datetime import date
from unittest.mock import patch

from games.base import BaseGame, Weekday
from notifiers.base import BaseNotifier
from main import main, should_notify_today


class FakeGame(BaseGame):
    name = "FakeGame"
    xml_url = "https://example.com/xml"
    draw_days = [Weekday.WEDNESDAY, Weekday.SATURDAY]
    prize_threshold = 1_000_000.0

    def fetch_jackpot(self) -> float | None:
        return 2_000_000.0


class MockNotifier(BaseNotifier):
    def __init__(self):
        self.calls = []

    def send(self, results):
        self.calls.append(results)


# should_notify_today — day before draw

def test_notifies_day_before_weekday_draw():
    game = FakeGame()
    # Wednesday draw -> Tuesday notify; 2026-05-26 is a Tuesday
    assert should_notify_today(game, date(2026, 5, 26)) is True


def test_notifies_day_before_saturday_draw():
    game = FakeGame()
    # Saturday draw -> Friday notify; 2026-05-29 is a Friday
    assert should_notify_today(game, date(2026, 5, 29)) is True


def test_does_not_notify_on_draw_day():
    game = FakeGame()
    # Wednesday is draw day, not notify day; 2026-05-27 is a Wednesday
    assert should_notify_today(game, date(2026, 5, 27)) is False


def test_does_not_notify_on_unrelated_day():
    game = FakeGame()
    # Thursday is neither draw day nor notify day; 2026-05-28 is a Thursday
    assert should_notify_today(game, date(2026, 5, 28)) is False


# main() loop

def test_qualifying_game_sends_notification():
    notifier = MockNotifier()
    with patch("main.games", [FakeGame()]), patch("main.notifiers", [notifier]), \
         patch("main.should_notify_today", return_value=True):
        main()
    assert notifier.calls == [[("FakeGame", 2_000_000.0, 1_000_000.0)]]


def test_game_below_threshold_no_notification():
    game = FakeGame()
    game.prize_threshold = 5_000_000.0  # above fetch_jackpot() return value
    notifier = MockNotifier()
    with patch("main.games", [game]), patch("main.notifiers", [notifier]), \
         patch("main.should_notify_today", return_value=True):
        main()
    assert notifier.calls == []


def test_not_notification_day_skips_fetch():
    notifier = MockNotifier()
    with patch("main.games", [FakeGame()]), patch("main.notifiers", [notifier]), \
         patch("main.should_notify_today", return_value=False):
        main()
    assert notifier.calls == []


def test_failed_fetch_skips_game():
    game = FakeGame()
    game.fetch_jackpot = lambda: None
    notifier = MockNotifier()
    with patch("main.games", [game]), patch("main.notifiers", [notifier]), \
         patch("main.should_notify_today", return_value=True):
        main()
    assert notifier.calls == []


def test_multiple_qualifying_games_batched():
    game1 = FakeGame()
    game1.name = "GameA"
    game1.prize_threshold = 1_000_000.0

    game2 = FakeGame()
    game2.name = "GameB"
    game2.prize_threshold = 1_000_000.0

    game3 = FakeGame()
    game3.name = "GameC"
    game3.prize_threshold = 5_000_000.0  # below jackpot — won't qualify

    notifier = MockNotifier()
    with patch("main.games", [game1, game2, game3]), patch("main.notifiers", [notifier]), \
         patch("main.should_notify_today", return_value=True):
        main()

    assert notifier.calls == [[
        ("GameA", 2_000_000.0, 1_000_000.0),
        ("GameB", 2_000_000.0, 1_000_000.0),
    ]]
