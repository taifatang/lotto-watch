from datetime import date
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


def test_notifies_on_day_after_weekday_draw(game):
    # Wednesday draw (2) -> Thursday notify (3); 2026-05-28 is a Thursday
    assert game.should_notify_today(date(2026, 5, 28)) is True


def test_notifies_on_monday_for_saturday_draw(game):
    # Saturday draw (5) -> Monday notify (0); 2026-05-25 is a Monday
    assert game.should_notify_today(date(2026, 5, 25)) is True


def test_does_not_notify_on_draw_day(game):
    # Wednesday is draw day, not notification day; 2026-05-27 is a Wednesday
    assert game.should_notify_today(date(2026, 5, 27)) is False


def test_does_not_notify_on_unrelated_day(game):
    # Tuesday maps to no draw_day for this game; 2026-05-26 is a Tuesday
    assert game.should_notify_today(date(2026, 5, 26)) is False


def test_fetch_jackpot_returns_float_on_success(game, requests_mock):
    requests_mock.get(game.xml_url, text=SAMPLE_XML)
    assert game.fetch_jackpot() == 12_500_000.0


def test_fetch_jackpot_returns_none_on_http_error(game, requests_mock):
    requests_mock.get(game.xml_url, status_code=403)
    assert game.fetch_jackpot() is None


def test_fetch_jackpot_returns_none_on_missing_element(game, requests_mock):
    requests_mock.get(game.xml_url, text="<draw-results><game></game></draw-results>")
    assert game.fetch_jackpot() is None
