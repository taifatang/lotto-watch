import pytest
from games.base import BaseGame, DrawData, Weekday


class FakeGame(BaseGame):
    name = "FakeGame"
    url = "https://example.com/xml"
    draw_days = [Weekday.WEDNESDAY]
    prize_threshold = 1_000_000.0

    def parse(self, xml_text: str) -> DrawData:
        return DrawData(jackpot=5_000_000.0, rollover_count=2)


@pytest.fixture
def game():
    return FakeGame()


def test_fetch_draw_data_calls_parse_on_success(game, requests_mock):
    requests_mock.get(game.url, text="<xml/>")
    data = game.fetch_draw_data()
    assert data == DrawData(jackpot=5_000_000.0, rollover_count=2)


def test_fetch_draw_data_returns_empty_on_http_error(game, requests_mock):
    requests_mock.get(game.url, status_code=403)
    assert game.fetch_draw_data() == DrawData(jackpot=None, rollover_count=None)
