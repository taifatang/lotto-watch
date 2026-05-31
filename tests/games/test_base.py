import pytest
from games.base import BaseGame


class ConcreteGame(BaseGame):
    name = "TestGame"
    xml_url = "https://example.com/xml"
    draw_days = [2, 5]  # Wednesday=2, Saturday=5
    threshold = 10_000_000.0


@pytest.fixture
def game():
    return ConcreteGame()


SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<draw-results>
  <game type="test">
    <draw><draw-date>2026-05-30</draw-date></draw>
    <next-estimated-jackpot>12,500,000</next-estimated-jackpot>
  </game>
</draw-results>"""


def test_fetch_jackpot_returns_float_on_success(game, requests_mock):
    requests_mock.get(game.xml_url, text=SAMPLE_XML)
    assert game.fetch_jackpot() == 12_500_000.0


def test_fetch_jackpot_returns_none_on_http_error(game, requests_mock):
    requests_mock.get(game.xml_url, status_code=403)
    assert game.fetch_jackpot() is None


def test_fetch_jackpot_returns_none_on_missing_element(game, requests_mock):
    requests_mock.get(game.xml_url, text="<draw-results><game></game></draw-results>")
    assert game.fetch_jackpot() is None
