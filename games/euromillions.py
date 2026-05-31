import xml.etree.ElementTree as ET

from games.base import BaseGame, DrawData, Weekday


class EuroMillions(BaseGame):
    name = "EuroMillions"
    url = "https://www.national-lottery.co.uk/results/euromillions/draw-history/xml"
    draw_days = [Weekday.TUESDAY, Weekday.FRIDAY]
    prize_threshold = 75_000_000.0

    def parse(self, xml_text: str) -> DrawData:
        root = ET.fromstring(xml_text)
        el = root.find(".//next-estimated-jackpot")
        jackpot = float(el.text.replace(",", "").strip()) if el is not None and el.text else None
        return DrawData(jackpot=jackpot, rollover_count=None)
