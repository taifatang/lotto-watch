from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

from games.base import GameData
from main import main, should_notify_today


class FakeGame:
    name = "FakeGame"
    emoji = "🎮"
    draw_days = [2, 5]  # Wednesday=2, Saturday=5
    prize_threshold = 1_000_000.0

    def fetch_draw_data(self):
        return GameData(jackpot=2_000_000.0, is_roll_down=None)


class MockNotifier:
    def __init__(self):
        self.calls = []

    def send(self, results):
        self.calls.append(results)


def fake_notifiers(notifier):
    return SimpleNamespace(live=[notifier], test=[])


EXPECTED_RESULT = ("🎮 FakeGame", 2_000_000.0, 1_000_000.0, [2, 5], None)

# should_notify_today — day before draw

def test_notifies_day_before_weekday_draw():
    # Wednesday draw -> Tuesday notify; 2026-05-26 is a Tuesday
    assert should_notify_today(FakeGame(), date(2026, 5, 26)) is True


def test_notifies_day_before_saturday_draw():
    # Saturday draw -> Friday notify; 2026-05-29 is a Friday
    assert should_notify_today(FakeGame(), date(2026, 5, 29)) is True


def test_does_not_notify_on_draw_day():
    # Wednesday is draw day, not notify day; 2026-05-27 is a Wednesday
    assert should_notify_today(FakeGame(), date(2026, 5, 27)) is False


def test_does_not_notify_on_unrelated_day():
    # Thursday is neither draw day nor notify day; 2026-05-28 is a Thursday
    assert should_notify_today(FakeGame(), date(2026, 5, 28)) is False


# main() loop

def test_qualifying_game_sends_notification():
    notifier = MockNotifier()
    with patch("main.games", [FakeGame()]), patch("main.notifiers", fake_notifiers(notifier)), \
         patch("main.should_notify_today", return_value=True):
        main()
    assert notifier.calls == [[EXPECTED_RESULT]]


def test_game_below_threshold_no_notification():
    game = FakeGame()
    game.prize_threshold = 5_000_000.0
    notifier = MockNotifier()
    with patch("main.games", [game]), patch("main.notifiers", fake_notifiers(notifier)), \
         patch("main.should_notify_today", return_value=True):
        main()
    assert notifier.calls == []


def test_game_qualifies_via_must_be_won():
    game = FakeGame()
    game.prize_threshold = 5_000_000.0  # jackpot won't qualify
    game.fetch_draw_data = lambda: GameData(jackpot=2_000_000.0, is_roll_down=True)
    notifier = MockNotifier()
    with patch("main.games", [game]), patch("main.notifiers", fake_notifiers(notifier)), \
         patch("main.should_notify_today", return_value=True):
        main()
    assert len(notifier.calls) == 1


def test_not_notification_day_skips_fetch():
    notifier = MockNotifier()
    with patch("main.games", [FakeGame()]), patch("main.notifiers", fake_notifiers(notifier)), \
         patch("main.should_notify_today", return_value=False):
        main()
    assert notifier.calls == []


def test_failed_fetch_skips_game():
    game = FakeGame()
    game.fetch_draw_data = lambda: GameData(jackpot=None)
    notifier = MockNotifier()
    with patch("main.games", [game]), patch("main.notifiers", fake_notifiers(notifier)), \
         patch("main.should_notify_today", return_value=True):
        main()
    assert notifier.calls == []


def test_multiple_qualifying_games_batched():
    game1, game2, game3 = FakeGame(), FakeGame(), FakeGame()
    game1.name, game1.prize_threshold = "GameA", 1_000_000.0
    game2.name, game2.prize_threshold = "GameB", 1_000_000.0
    game3.name, game3.prize_threshold = "GameC", 5_000_000.0  # won't qualify

    notifier = MockNotifier()
    with patch("main.games", [game1, game2, game3]), patch("main.notifiers", fake_notifiers(notifier)), \
         patch("main.should_notify_today", return_value=True):
        main()

    assert notifier.calls == [[
        ("🎮 GameA", 2_000_000.0, 1_000_000.0, [2, 5], None),
        ("🎮 GameB", 2_000_000.0, 1_000_000.0, [2, 5], None),
    ]]
