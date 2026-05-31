import xml.etree.ElementTree as ET

from games.base import BaseGame, DrawData, Weekday


class Lotto(BaseGame):
    name = "Lotto"
    url = "https://www.national-lottery.co.uk/results/lotto/draw-history/xml"
    draw_days = [Weekday.WEDNESDAY, Weekday.SATURDAY]
    prize_threshold = 5_000_000.0

    def parse(self, xml_text: str) -> DrawData:
        root = ET.fromstring(xml_text)
        jackpot_el = root.find(".//next-estimated-jackpot")
        rolldown_el = root.find(".//next-estimated-jackpot-roll-down")
        jackpot = float(jackpot_el.text.replace(",", "").strip()) if jackpot_el is not None and jackpot_el.text else None
        is_roll_down = rolldown_el is not None and rolldown_el.text == "Y"
        return DrawData(jackpot=jackpot, is_roll_down=is_roll_down)
