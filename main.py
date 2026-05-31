from datetime import date

from games.base import Weekday


def should_notify_today(game, today: date | None = None) -> bool:
    today = today or date.today()
    for draw_day in game.draw_days:
        notify_day = Weekday.MONDAY if draw_day >= Weekday.FRIDAY else Weekday(draw_day + 1)
        if today.weekday() == notify_day:
            return True
    return False


games = []
notifiers = []


def main():
    qualifying = []
    for game in games:
        if not should_notify_today(game):
            continue
        jackpot = game.fetch_jackpot()
        if jackpot is not None and jackpot >= game.prize_threshold:
            qualifying.append((game.name, jackpot, game.prize_threshold))

    if qualifying:
        for notifier in notifiers:
            notifier.send(qualifying)
    else:
        print("No qualifying games today.")


if __name__ == "__main__":
    main()
