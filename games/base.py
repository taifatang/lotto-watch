from abc import ABC
import xml.etree.ElementTree as ET
import requests


class BaseGame(ABC):
    name: str
    xml_url: str
    draw_days: list[int]  # Mon=0 ... Sun=6
    threshold: float      # pounds

    _headers: dict = {"User-Agent": "Mozilla/5.0 (compatible; NationalLotteryNotifier/1.0)"}

    def fetch_jackpot(self) -> float | None:
        try:
            response = requests.get(self.xml_url, headers=self._headers, timeout=10)
            response.raise_for_status()
            return self._parse_xml(response.text)
        except Exception as e:
            print(f"[{self.name}] fetch failed: {e}")
            return None

    def _parse_xml(self, xml_text: str) -> float | None:
        try:
            root = ET.fromstring(xml_text)
            el = root.find(".//next-estimated-jackpot")
            if el is None or el.text is None:
                print(f"[{self.name}] <next-estimated-jackpot> not found")
                return None
            cleaned = el.text.replace(",", "").strip()
            return float(cleaned)
        except Exception as e:
            print(f"[{self.name}] parse failed: {e}")
            return None
