from datetime import date
from types import SimpleNamespace

from games.base import Weekday
from games.euromillions import EuroMillions
from games.lotto import Lotto
from notifiers.console_notifier import ConsoleNotifier


def should_notify_today(game, today: date | None = None) -> bool:
    today = today or date.today()
    for draw_day in game.draw_days:
        notify_day = Weekday((draw_day - 1) % 7)
        if today.weekday() == notify_day:
            return True
    return False


games = [EuroMillions(), Lotto()]
notifiers = SimpleNamespace(
    test=[ConsoleNotifier()],
    live=[],
)


def main(test=False):
    active_notifiers = notifiers.test if test else notifiers.live

    if not active_notifiers:
        print("No notifiers installed.")
        return

    high_prized_games = []
    for game in games:
        if not test and not should_notify_today(game):
            continue
        data = game.fetch_draw_data()
        jackpot_qualifies = data.jackpot is not None and data.jackpot >= game.prize_threshold
        rollover_qualifies = (
            game.max_rollovers is not None
            and data.rollover_count is not None
            and data.rollover_count >= game.max_rollovers
        )
        if jackpot_qualifies or rollover_qualifies:
            high_prized_games.append((
                game.name,
                data.jackpot,
                game.prize_threshold,
                game.draw_days,
                data.rollover_count,
                game.max_rollovers,
            ))

    if high_prized_games:
        for notifier in active_notifiers:
            notifier.send(high_prized_games)
    else:
        print("No games with good prizes.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    main(test=args.test)
