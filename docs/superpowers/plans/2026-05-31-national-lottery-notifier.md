# National Lottery High Prize Notifier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Monitor UK National Lottery jackpots via XML API and send a single batched Telegram notification on the next working day after each draw, when any game's estimated jackpot exceeds its per-game threshold.

**Architecture:** Each game subclasses `BaseGame`, which implements shared HTTP fetch, XML parse, and notification-day logic. `main.py` collects qualifying games then dispatches one message through each notifier. GitHub Actions runs the script Mon–Fri at 9am UTC.

**Tech Stack:** Python 3.11+, `requests`, `xml.etree.ElementTree` (stdlib), `pytest`, `requests-mock`, GitHub Actions, Telegram Bot API.

---

## File Map

| File | Responsibility |
|---|---|
| `pyproject.toml` | Project metadata and dependencies |
| `games/base.py` | `BaseGame` ABC: `should_notify_today()`, `fetch_jackpot()`, `_parse_xml()` |
| `games/lotto.py` | `Lotto`: name, url, `draw_days=[2,5]`, threshold |
| `games/euromillions.py` | `EuroMillions`: name, url, `draw_days=[1,4]`, threshold |
| `games/set_for_life.py` | `SetForLife`: name, url, `draw_days=[0,3]`, threshold |
| `games/thunderball.py` | `Thunderball`: name, url, `draw_days=[1,2,4,5]`, threshold |
| `notifiers/base.py` | `BaseNotifier` ABC: `send()` |
| `notifiers/telegram.py` | `TelegramNotifier`: reads env vars, POSTs to Telegram API |
| `main.py` | Entry point: loop games → collect qualifying → dispatch notifiers |
| `.github/workflows/notify.yml` | GitHub Actions cron schedule |
| `tests/games/test_base.py` | Tests for `should_notify_today()` and `fetch_jackpot()` |
| `tests/games/test_lotto.py` | Tests for `Lotto` attributes and XML parsing |
| `tests/games/test_euromillions.py` | Tests for `EuroMillions` |
| `tests/games/test_set_for_life.py` | Tests for `SetForLife` |
| `tests/games/test_thunderball.py` | Tests for `Thunderball` |
| `tests/notifiers/test_telegram.py` | Tests for `TelegramNotifier.send()` |
| `tests/test_main.py` | Integration tests for `main()` loop |

---

### Task 1: Project Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `games/__init__.py`
- Create: `notifiers/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/games/__init__.py`
- Create: `tests/notifiers/__init__.py`

- [ ] **Step 1: Create directories**

```bash
mkdir -p games notifiers tests/games tests/notifiers .github/workflows
```

- [ ] **Step 2: Create pyproject.toml**

```toml
[project]
name = "national-lottery-notifier"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["requests>=2.31.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "requests-mock>=1.11.0"]
```

- [ ] **Step 3: Create empty __init__.py files**

```bash
touch games/__init__.py notifiers/__init__.py tests/__init__.py tests/games/__init__.py tests/notifiers/__init__.py
```

- [ ] **Step 4: Install dependencies**

```bash
pip install requests pytest requests-mock
```

Expected: `Successfully installed` for all packages.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml games/__init__.py notifiers/__init__.py tests/__init__.py tests/games/__init__.py tests/notifiers/__init__.py
git commit -m "chore: project scaffold"
```

---

### Task 2: BaseGame ABC

**Files:**
- Create: `games/base.py`
- Create: `tests/games/test_base.py`

- [ ] **Step 1: Inspect actual XML structure**

Fetch real XML to confirm element names before writing any parser:

```bash
curl -s -A "Mozilla/5.0 (compatible; NationalLotteryNotifier/1.0)" \
  "https://www.national-lottery.co.uk/results/lotto/draw-history/xml" | head -60
```

Look for the element containing the next estimated jackpot (expected: `nextEstimatedJackpot`). Note whether values are integers (pence or pounds) or decimals. If the element name differs from `nextEstimatedJackpot`, update `_jackpot_xml_tag` in `BaseGame` before proceeding.

- [ ] **Step 2: Write failing tests**

`tests/games/test_base.py`:
```python
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


SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<draws>
  <draw>
    <drawDate>27-May-2026</drawDate>
    <jackpot>7500000.00</jackpot>
    <nextEstimatedJackpot>12500000.00</nextEstimatedJackpot>
  </draw>
</draws>"""


def test_notifies_on_day_after_weekday_draw(game):
    # Wednesday draw (2) → Thursday notify (3); 2026-05-28 is a Thursday
    assert game.should_notify_today(date(2026, 5, 28)) is True


def test_notifies_on_monday_for_saturday_draw(game):
    # Saturday draw (5) → Monday notify (0); 2026-05-25 is a Monday
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
    xml = "<draws><draw><jackpot>1000.00</jackpot></draw></draws>"
    requests_mock.get(game.xml_url, text=xml)
    assert game.fetch_jackpot() is None
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
pytest tests/games/test_base.py -v
```

Expected: `ImportError: cannot import name 'BaseGame' from 'games.base'`

- [ ] **Step 4: Implement BaseGame**

`games/base.py`:
```python
from abc import ABC
from datetime import date
import xml.etree.ElementTree as ET
import requests


class BaseGame(ABC):
    name: str
    xml_url: str
    draw_days: list[int]
    threshold: float
    _jackpot_xml_tag: str = "nextEstimatedJackpot"
    _headers: dict = {"User-Agent": "Mozilla/5.0 (compatible; NationalLotteryNotifier/1.0)"}

    def should_notify_today(self, today: date | None = None) -> bool:
        today = today or date.today()
        today_weekday = today.weekday()
        for draw_day in self.draw_days:
            notify_day = 0 if draw_day >= 4 else draw_day + 1
            if today_weekday == notify_day:
                return True
        return False

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
            draw = root.find(".//draw")
            if draw is None:
                print(f"[{self.name}] no <draw> element in XML")
                return None
            el = draw.find(self._jackpot_xml_tag)
            if el is None or el.text is None:
                print(f"[{self.name}] <{self._jackpot_xml_tag}> not found")
                return None
            return float(el.text)
        except Exception as e:
            print(f"[{self.name}] parse failed: {e}")
            return None
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/games/test_base.py -v
```

Expected: all 7 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add games/base.py tests/games/test_base.py
git commit -m "feat: add BaseGame ABC with notification-day logic and XML fetcher"
```

---

### Task 3: BaseNotifier ABC

**Files:**
- Create: `notifiers/base.py`

- [ ] **Step 1: Implement BaseNotifier**

`notifiers/base.py`:
```python
from abc import ABC, abstractmethod


class BaseNotifier(ABC):
    @abstractmethod
    def send(self, results: list[tuple[str, float, float]]) -> None:
        """Send notification for qualifying games.

        results: list of (game_name, jackpot_pounds, threshold_pounds)
        """
```

- [ ] **Step 2: Commit**

```bash
git add notifiers/base.py
git commit -m "feat: add BaseNotifier ABC"
```

---

### Task 4: TelegramNotifier

**Files:**
- Create: `notifiers/telegram.py`
- Create: `tests/notifiers/test_telegram.py`

- [ ] **Step 1: Write failing tests**

`tests/notifiers/test_telegram.py`:
```python
import pytest
from notifiers.telegram import TelegramNotifier

RESULTS = [
    ("EuroMillions", 95_000_000.0, 50_000_000.0),
    ("Lotto", 12_500_000.0, 10_000_000.0),
]

EXPECTED_MESSAGE = (
    "🎰 High prizes today!\n"
    "• EuroMillions: £95,000,000.00 (threshold: £50,000,000.00)\n"
    "• Lotto: £12,500,000.00 (threshold: £10,000,000.00)"
)


@pytest.fixture
def notifier(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123456")
    return TelegramNotifier()


def test_sends_correct_message(notifier, requests_mock):
    requests_mock.post(
        "https://api.telegram.org/bottest-token/sendMessage",
        json={"ok": True},
    )
    notifier.send(RESULTS)
    assert requests_mock.last_request.json() == {
        "chat_id": "123456",
        "text": EXPECTED_MESSAGE,
    }


def test_send_does_not_raise_on_http_error(notifier, requests_mock):
    requests_mock.post(
        "https://api.telegram.org/bottest-token/sendMessage",
        status_code=400,
    )
    notifier.send(RESULTS)  # must not raise
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/notifiers/test_telegram.py -v
```

Expected: `ImportError: cannot import name 'TelegramNotifier'`

- [ ] **Step 3: Implement TelegramNotifier**

`notifiers/telegram.py`:
```python
import os
import requests
from notifiers.base import BaseNotifier


class TelegramNotifier(BaseNotifier):
    _api_url = "https://api.telegram.org/bot{token}/sendMessage"

    def send(self, results: list[tuple[str, float, float]]) -> None:
        token = os.environ["TELEGRAM_BOT_TOKEN"]
        chat_id = os.environ["TELEGRAM_CHAT_ID"]

        lines = ["🎰 High prizes today!"]
        for game_name, jackpot, threshold in results:
            lines.append(f"• {game_name}: £{jackpot:,.2f} (threshold: £{threshold:,.2f})")
        message = "\n".join(lines)

        try:
            response = requests.post(
                self._api_url.format(token=token),
                json={"chat_id": chat_id, "text": message},
                timeout=10,
            )
            response.raise_for_status()
            print("Telegram notification sent.")
        except Exception as e:
            print(f"Telegram send failed: {e}")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/notifiers/test_telegram.py -v
```

Expected: all 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add notifiers/telegram.py tests/notifiers/test_telegram.py
git commit -m "feat: add TelegramNotifier"
```

---

### Task 5: Lotto game

**Files:**
- Create: `games/lotto.py`
- Create: `tests/games/test_lotto.py`

- [ ] **Step 1: Write failing tests**

`tests/games/test_lotto.py`:
```python
from datetime import date
from games.lotto import Lotto

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<draws>
  <draw>
    <drawDate>27-May-2026</drawDate>
    <jackpot>7500000.00</jackpot>
    <nextEstimatedJackpot>12500000.00</nextEstimatedJackpot>
  </draw>
</draws>"""


def test_lotto_attributes():
    game = Lotto()
    assert game.name == "Lotto"
    assert "lotto" in game.xml_url
    assert 2 in game.draw_days   # Wednesday
    assert 5 in game.draw_days   # Saturday
    assert game.threshold > 0


def test_lotto_notifies_on_thursday():
    # Wednesday draw (2) → Thursday notify (3); 2026-05-28 is a Thursday
    assert Lotto().should_notify_today(date(2026, 5, 28)) is True


def test_lotto_notifies_on_monday():
    # Saturday draw (5) → Monday notify (0); 2026-05-25 is a Monday
    assert Lotto().should_notify_today(date(2026, 5, 25)) is True


def test_lotto_does_not_notify_on_wednesday():
    # Wednesday is draw day, not notification day; 2026-05-27 is a Wednesday
    assert Lotto().should_notify_today(date(2026, 5, 27)) is False


def test_lotto_fetch_jackpot(requests_mock):
    game = Lotto()
    requests_mock.get(game.xml_url, text=SAMPLE_XML)
    assert game.fetch_jackpot() == 12_500_000.0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/games/test_lotto.py -v
```

Expected: `ImportError: cannot import name 'Lotto'`

- [ ] **Step 3: Implement Lotto**

`games/lotto.py`:
```python
from games.base import BaseGame


class Lotto(BaseGame):
    name = "Lotto"
    xml_url = "https://www.national-lottery.co.uk/results/lotto/draw-history/xml"
    draw_days = [2, 5]  # Wednesday=2, Saturday=5
    threshold = 5_000_000.0
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/games/test_lotto.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add games/lotto.py tests/games/test_lotto.py
git commit -m "feat: add Lotto game"
```

---

### Task 6: EuroMillions game

**Files:**
- Create: `games/euromillions.py`
- Create: `tests/games/test_euromillions.py`

- [ ] **Step 1: Write failing tests**

`tests/games/test_euromillions.py`:
```python
from datetime import date
from games.euromillions import EuroMillions

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<draws>
  <draw>
    <drawDate>29-May-2026</drawDate>
    <jackpot>75000000.00</jackpot>
    <nextEstimatedJackpot>95000000.00</nextEstimatedJackpot>
  </draw>
</draws>"""


def test_euromillions_attributes():
    game = EuroMillions()
    assert game.name == "EuroMillions"
    assert "euromillions" in game.xml_url
    assert 1 in game.draw_days   # Tuesday
    assert 4 in game.draw_days   # Friday
    assert game.threshold > 0


def test_euromillions_notifies_on_wednesday():
    # Tuesday draw (1) → Wednesday notify (2); 2026-05-27 is a Wednesday
    assert EuroMillions().should_notify_today(date(2026, 5, 27)) is True


def test_euromillions_notifies_on_monday():
    # Friday draw (4) → Monday notify (0); 2026-05-25 is a Monday
    assert EuroMillions().should_notify_today(date(2026, 5, 25)) is True


def test_euromillions_does_not_notify_on_friday():
    # Friday is draw day, not notification day; 2026-05-29 is a Friday
    assert EuroMillions().should_notify_today(date(2026, 5, 29)) is False


def test_euromillions_fetch_jackpot(requests_mock):
    game = EuroMillions()
    requests_mock.get(game.xml_url, text=SAMPLE_XML)
    assert game.fetch_jackpot() == 95_000_000.0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/games/test_euromillions.py -v
```

Expected: `ImportError: cannot import name 'EuroMillions'`

- [ ] **Step 3: Implement EuroMillions**

`games/euromillions.py`:
```python
from games.base import BaseGame


class EuroMillions(BaseGame):
    name = "EuroMillions"
    xml_url = "https://www.national-lottery.co.uk/results/euromillions/draw-history/xml"
    draw_days = [1, 4]  # Tuesday=1, Friday=4
    threshold = 50_000_000.0
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/games/test_euromillions.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add games/euromillions.py tests/games/test_euromillions.py
git commit -m "feat: add EuroMillions game"
```

---

### Task 7: Set For Life game

**Files:**
- Create: `games/set_for_life.py`
- Create: `tests/games/test_set_for_life.py`

- [ ] **Step 1: Write failing tests**

`tests/games/test_set_for_life.py`:
```python
from datetime import date
from games.set_for_life import SetForLife

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<draws>
  <draw>
    <drawDate>25-May-2026</drawDate>
    <jackpot>3600000.00</jackpot>
    <nextEstimatedJackpot>3600000.00</nextEstimatedJackpot>
  </draw>
</draws>"""


def test_set_for_life_attributes():
    game = SetForLife()
    assert game.name == "Set For Life"
    assert "set-for-life" in game.xml_url
    assert 0 in game.draw_days   # Monday
    assert 3 in game.draw_days   # Thursday
    assert game.threshold > 0


def test_set_for_life_notifies_on_tuesday():
    # Monday draw (0) → Tuesday notify (1); 2026-05-26 is a Tuesday
    assert SetForLife().should_notify_today(date(2026, 5, 26)) is True


def test_set_for_life_notifies_on_friday():
    # Thursday draw (3) → Friday notify (4); 2026-05-29 is a Friday
    assert SetForLife().should_notify_today(date(2026, 5, 29)) is True


def test_set_for_life_does_not_notify_on_monday():
    # No draw day maps to Monday for this game; 2026-05-25 is a Monday
    assert SetForLife().should_notify_today(date(2026, 5, 25)) is False


def test_set_for_life_fetch_jackpot(requests_mock):
    game = SetForLife()
    requests_mock.get(game.xml_url, text=SAMPLE_XML)
    assert game.fetch_jackpot() == 3_600_000.0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/games/test_set_for_life.py -v
```

Expected: `ImportError: cannot import name 'SetForLife'`

- [ ] **Step 3: Implement SetForLife**

`games/set_for_life.py`:
```python
from games.base import BaseGame


class SetForLife(BaseGame):
    name = "Set For Life"
    xml_url = "https://www.national-lottery.co.uk/results/set-for-life/draw-history/xml"
    draw_days = [0, 3]  # Monday=0, Thursday=3
    threshold = 3_600_000.0
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/games/test_set_for_life.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add games/set_for_life.py tests/games/test_set_for_life.py
git commit -m "feat: add Set For Life game"
```

---

### Task 8: Thunderball game

**Files:**
- Create: `games/thunderball.py`
- Create: `tests/games/test_thunderball.py`

- [ ] **Step 1: Write failing tests**

`tests/games/test_thunderball.py`:
```python
from datetime import date
from games.thunderball import Thunderball

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<draws>
  <draw>
    <drawDate>29-May-2026</drawDate>
    <jackpot>500000.00</jackpot>
    <nextEstimatedJackpot>500000.00</nextEstimatedJackpot>
  </draw>
</draws>"""


def test_thunderball_attributes():
    game = Thunderball()
    assert game.name == "Thunderball"
    assert "thunderball" in game.xml_url
    assert 1 in game.draw_days   # Tuesday
    assert 2 in game.draw_days   # Wednesday
    assert 4 in game.draw_days   # Friday
    assert 5 in game.draw_days   # Saturday
    assert game.threshold > 0


def test_thunderball_notifies_on_wednesday():
    # Tuesday draw (1) → Wednesday notify (2); 2026-05-27 is a Wednesday
    assert Thunderball().should_notify_today(date(2026, 5, 27)) is True


def test_thunderball_notifies_on_thursday():
    # Wednesday draw (2) → Thursday notify (3); 2026-05-28 is a Thursday
    assert Thunderball().should_notify_today(date(2026, 5, 28)) is True


def test_thunderball_notifies_on_monday():
    # Friday/Saturday draws → Monday notify (0); 2026-05-25 is a Monday
    assert Thunderball().should_notify_today(date(2026, 5, 25)) is True


def test_thunderball_does_not_notify_on_tuesday():
    # No draw day maps to Tuesday for Thunderball; 2026-05-26 is a Tuesday
    assert Thunderball().should_notify_today(date(2026, 5, 26)) is False


def test_thunderball_fetch_jackpot(requests_mock):
    game = Thunderball()
    requests_mock.get(game.xml_url, text=SAMPLE_XML)
    assert game.fetch_jackpot() == 500_000.0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/games/test_thunderball.py -v
```

Expected: `ImportError: cannot import name 'Thunderball'`

- [ ] **Step 3: Implement Thunderball**

`games/thunderball.py`:
```python
from games.base import BaseGame


class Thunderball(BaseGame):
    name = "Thunderball"
    xml_url = "https://www.national-lottery.co.uk/results/thunderball/draw-history/xml"
    draw_days = [1, 2, 4, 5]  # Tuesday=1, Wednesday=2, Friday=4, Saturday=5
    threshold = 500_000.0
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/games/test_thunderball.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add games/thunderball.py tests/games/test_thunderball.py
git commit -m "feat: add Thunderball game"
```

---

### Task 9: main.py

**Files:**
- Create: `main.py`
- Create: `tests/test_main.py`

- [ ] **Step 1: Write failing tests**

`tests/test_main.py`:
```python
from unittest.mock import MagicMock, patch
from main import main


def make_game(name, notify, jackpot, threshold):
    game = MagicMock()
    game.name = name
    game.should_notify_today.return_value = notify
    game.fetch_jackpot.return_value = jackpot
    game.threshold = threshold
    return game


def test_qualifying_game_triggers_notification():
    game = make_game("Lotto", notify=True, jackpot=15_000_000.0, threshold=10_000_000.0)
    notifier = MagicMock()

    with patch("main.GAMES", [game]), patch("main.NOTIFIERS", [notifier]):
        main()

    notifier.send.assert_called_once_with([("Lotto", 15_000_000.0, 10_000_000.0)])


def test_game_below_threshold_not_notified():
    game = make_game("Lotto", notify=True, jackpot=5_000_000.0, threshold=10_000_000.0)
    notifier = MagicMock()

    with patch("main.GAMES", [game]), patch("main.NOTIFIERS", [notifier]):
        main()

    notifier.send.assert_not_called()


def test_game_not_on_notification_day_skipped():
    game = make_game("Lotto", notify=False, jackpot=15_000_000.0, threshold=10_000_000.0)
    notifier = MagicMock()

    with patch("main.GAMES", [game]), patch("main.NOTIFIERS", [notifier]):
        main()

    game.fetch_jackpot.assert_not_called()
    notifier.send.assert_not_called()


def test_failed_fetch_skips_game():
    game = make_game("Lotto", notify=True, jackpot=None, threshold=10_000_000.0)
    notifier = MagicMock()

    with patch("main.GAMES", [game]), patch("main.NOTIFIERS", [notifier]):
        main()

    notifier.send.assert_not_called()


def test_multiple_qualifying_games_batched():
    game1 = make_game("Lotto", notify=True, jackpot=15_000_000.0, threshold=10_000_000.0)
    game2 = make_game("EuroMillions", notify=True, jackpot=95_000_000.0, threshold=50_000_000.0)
    game3 = make_game("Thunderball", notify=True, jackpot=300_000.0, threshold=500_000.0)
    notifier = MagicMock()

    with patch("main.GAMES", [game1, game2, game3]), patch("main.NOTIFIERS", [notifier]):
        main()

    notifier.send.assert_called_once_with([
        ("Lotto", 15_000_000.0, 10_000_000.0),
        ("EuroMillions", 95_000_000.0, 50_000_000.0),
    ])
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_main.py -v
```

Expected: `ModuleNotFoundError: No module named 'main'`

- [ ] **Step 3: Implement main.py**

`main.py`:
```python
from games.lotto import Lotto
from games.euromillions import EuroMillions
from games.set_for_life import SetForLife
from games.thunderball import Thunderball
from notifiers.telegram import TelegramNotifier

GAMES = [Lotto(), EuroMillions(), SetForLife(), Thunderball()]
NOTIFIERS = [TelegramNotifier()]


def main():
    qualifying = []
    for game in GAMES:
        if not game.should_notify_today():
            continue
        jackpot = game.fetch_jackpot()
        if jackpot is not None and jackpot >= game.threshold:
            qualifying.append((game.name, jackpot, game.threshold))

    if qualifying:
        for notifier in NOTIFIERS:
            notifier.send(qualifying)
    else:
        print("No qualifying games today.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_main.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Run full test suite**

```bash
pytest -v
```

Expected: all tests PASS, 0 failures.

- [ ] **Step 6: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: add main entrypoint"
```

---

### Task 10: GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/notify.yml`

- [ ] **Step 1: Write workflow**

`.github/workflows/notify.yml`:
```yaml
name: National Lottery Prize Notifier

on:
  schedule:
    - cron: '0 9 * * 1-5'
  workflow_dispatch:

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install requests

      - name: Run notifier
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python main.py
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/notify.yml
git commit -m "ci: add GitHub Actions cron workflow"
```

- [ ] **Step 3: Add GitHub secrets**

In repo Settings → Secrets and variables → Actions, add:
- `TELEGRAM_BOT_TOKEN` — from @BotFather on Telegram
- `TELEGRAM_CHAT_ID` — your chat or group ID (get via `https://api.telegram.org/bot<TOKEN>/getUpdates` after sending a message)

- [ ] **Step 4: Test via workflow_dispatch**

GitHub → Actions → "National Lottery Prize Notifier" → Run workflow. Check logs. If no games qualify today, expected output: `No qualifying games today.`
