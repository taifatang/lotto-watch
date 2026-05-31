from datetime import date

from games.base import Weekday
from notifiers.github_console_notifier import GithubConsoleNotifier


def should_notify_today(game, today: date | None = None) -> bool:
    today = today or date.today()
    for draw_day in game.draw_days:
        notify_day = Weekday((draw_day - 1) % 7)
        if today.weekday() == notify_day:
            return True
    return False


games = []
notifiers = [GithubConsoleNotifier()]


def main(dry_run=False):
    active_notifiers = [GithubConsoleNotifier()] if dry_run else notifiers

    if not active_notifiers:
        print("No notifiers installed.")
        return

    high_prized_games = []
    for game in games:
        if not should_notify_today(game):
            continue
        jackpot = game.fetch_jackpot()
        if jackpot is not None and jackpot >= game.prize_threshold:
            high_prized_games.append((game.name, jackpot, game.prize_threshold))

    if high_prized_games:
        for notifier in active_notifiers:
            notifier.send(high_prized_games)
    else:
        print("No games with good prizes.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
