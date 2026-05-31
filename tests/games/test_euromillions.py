from games.base import DrawData
from games.euromillions import EuroMillions

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<draw-results>
  <game type="euromillions">
    <draw><draw-date>2026-05-29</draw-date></draw>
    <next-estimated-jackpot>122,000,000</next-estimated-jackpot>
  </game>
</draw-results>"""


def test_parse_returns_jackpot_with_no_rollover_count():
    data = EuroMillions().parse(SAMPLE_XML)
    assert data == DrawData(jackpot=122_000_000.0, rollover_count=None)
