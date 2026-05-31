from datetime import date


def should_notify_today(game, today: date | None = None) -> bool:
    today = today or date.today()
    for draw_day in game.draw_days:
        notify_day = 0 if draw_day >= 4 else draw_day + 1
        if today.weekday() == notify_day:
            return True
    return False


def main(games=None, notifiers=None):
    if games is None:
        from games.lotto import Lotto
        from games.euromillions import EuroMillions
        from games.set_for_life import SetForLife
        from games.thunderball import Thunderball
        games = [Lotto(), EuroMillions(), SetForLife(), Thunderball()]

    if notifiers is None:
        from notifiers.telegram import TelegramNotifier
        notifiers = [TelegramNotifier()]

    qualifying = []
    for game in games:
        if not should_notify_today(game):
            continue
        jackpot = game.fetch_jackpot()
        if jackpot is not None and jackpot >= game.threshold:
            qualifying.append((game.name, jackpot, game.threshold))

    if qualifying:
        for notifier in notifiers:
            notifier.send(qualifying)
    else:
        print("No qualifying games today.")


if __name__ == "__main__":
    main()
