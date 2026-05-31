from games.base import BaseGame, Weekday


class Lotto(BaseGame):
    name = "Lotto"
    url = "https://www.national-lottery.co.uk/results/lotto/draw-history/xml"
    draw_days = [Weekday.WEDNESDAY, Weekday.SATURDAY]
    prize_threshold = 5_000_000.0
    max_rollovers = 5
