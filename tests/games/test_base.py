import pytest
from games.base import BaseGame, DrawData, Weekday


class ConcreteGame(BaseGame):
    name = "TestGame"
    url = "https://example.com/xml"
    draw_days = [Weekday.WEDNESDAY, Weekday.SATURDAY]
    prize_threshold = 10_000_000.0


@pytest.fixture
def game():
    return ConcreteGame()


SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<draw-results>
  <game type="test">
    <draw><draw-date>2026-05-30</draw-date></draw>
    <next-estimated-jackpot>12,500,000</next-estimated-jackpot>
    <rollover-count>3</rollover-count>
  </game>
</draw-results>"""


def test_fetch_draw_data_returns_jackpot_and_rollover(game, requests_mock):
    requests_mock.get(game.url, text=SAMPLE_XML)
    data = game.fetch_draw_data()
    assert data.jackpot == 12_500_000.0
    assert data.rollover_count == 3


def test_fetch_draw_data_returns_none_on_http_error(game, requests_mock):
    requests_mock.get(game.url, status_code=403)
    data = game.fetch_draw_data()
    assert data == DrawData(jackpot=None, rollover_count=None)


def test_fetch_draw_data_returns_none_jackpot_on_missing_element(game, requests_mock):
    requests_mock.get(game.url, text="<draw-results><game></game></draw-results>")
    data = game.fetch_draw_data()
    assert data.jackpot is None
