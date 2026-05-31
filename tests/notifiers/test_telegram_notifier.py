import pytest
from notifiers.telegram_notifier import TelegramNotifier

RESULTS = [
    ("EuroMillions", 95_000_000.0, 75_000_000.0, [1, 4], None),
    ("Lotto", 20_000_000.0, 5_000_000.0, [2, 5], True),
]


@pytest.fixture
def notifier(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123456")
    return TelegramNotifier()


def test_sends_message_with_must_be_won_flag(notifier, requests_mock):
    requests_mock.post(
        "https://api.telegram.org/bottest-token/sendMessage",
        json={"ok": True},
    )
    notifier.send(RESULTS)
    text = requests_mock.last_request.json()["text"]
    assert "EuroMillions" in text
    assert "Lotto" in text
    assert "(Must-be-won draw)" in text


def test_send_does_not_raise_on_http_error(notifier, requests_mock):
    requests_mock.post(
        "https://api.telegram.org/bottest-token/sendMessage",
        status_code=400,
    )
    notifier.send(RESULTS)  # must not raise
