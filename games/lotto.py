import xml.etree.ElementTree as ET

from games.base import BaseGame, DrawData, Weekday


class Lotto(BaseGame):
    name = "Lotto"
    url = "https://www.national-lottery.co.uk/results/lotto/draw-history/xml"
    draw_days = [Weekday.WEDNESDAY, Weekday.SATURDAY]
    prize_threshold = 5_000_000.0
    max_rollovers = 5

    def parse(self, xml_text: str) -> DrawData:
        root = ET.fromstring(xml_text)
        jackpot_el = root.find(".//next-estimated-jackpot")
        rollover_el = root.find(".//rollover-count")
        jackpot = float(jackpot_el.text.replace(",", "").strip()) if jackpot_el is not None and jackpot_el.text else None
        rollover_count = int(rollover_el.text) if rollover_el is not None and rollover_el.text else None
        return DrawData(jackpot=jackpot, rollover_count=rollover_count)
