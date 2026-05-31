import xml.etree.ElementTree as ET

from games.base import BaseGame, GameData, Weekday


class EuroMillions(BaseGame):
    name = "EuroMillions"
    emoji = "🌟"
    url = "https://www.national-lottery.co.uk/results/euromillions/draw-history/xml"
    draw_days = [Weekday.TUESDAY, Weekday.FRIDAY]
    prize_threshold = 75_000_000.0

    def parse(self, xml_text: str) -> GameData:
        root = ET.fromstring(xml_text)
        el = root.find(".//next-estimated-jackpot")
        jackpot = float(el.text.replace(",", "").strip()) if el is not None and el.text else None
        return GameData(jackpot=jackpot)
