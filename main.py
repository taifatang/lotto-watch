from datetime import date

from games.base import Weekday


def should_notify_today(game, today: date | None = None) -> bool:
    today = today or date.today()
    for draw_day in game.draw_days:
        notify_day = Weekday((draw_day - 1) % 7)
        if today.weekday() == notify_day:
            return True
    return False


games = []
notifiers = []


def main():
    high_prized_games = []
    for game in games:
        if not should_notify_today(game):
            continue
        jackpot = game.fetch_jackpot()
        if jackpot is not None and jackpot >= game.prize_threshold:
            high_prized_games.append((game.name, jackpot, game.prize_threshold))

    if not notifiers:
        print("No notifiers installed.")
        return

    if high_prized_games:
        for notifier in notifiers:
            notifier.send(high_prized_games)
    else:
        print("No games with good prizes.")


if __name__ == "__main__":
    main()
