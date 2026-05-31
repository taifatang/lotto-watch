# National Lottery High Prize Notifier — Design Spec

**Date:** 2026-05-31  
**Status:** Approved

---

## Overview

A Python cron job (GitHub Actions, Mon–Fri) that monitors UK National Lottery jackpots. On the working day after each game's draw day, it checks the estimated next jackpot against a per-game threshold. If any games exceed their threshold, a single batched Telegram message is sent.

---

## Project Structure

```
national-lottery-high-prize-notifier/
├── games/
│   ├── base.py          # BaseGame ABC
│   ├── lotto.py
│   ├── euromillions.py
│   ├── set_for_life.py
│   └── thunderball.py
├── notifiers/
│   ├── base.py          # BaseNotifier ABC
│   └── telegram.py
├── main.py
├── .github/
│   └── workflows/
│       └── notify.yml
└── pyproject.toml
```

---

## BaseGame (ABC)

Each game subclass lives in `games/` and defines all its own config. No external config file.

### Required attributes

| Attribute | Type | Description |
|---|---|---|
| `name` | `str` | Display name (e.g. `"EuroMillions"`) |
| `xml_url` | `str` | National Lottery draw history XML endpoint |
| `draw_days` | `list[int]` | Weekday ints Mon=0 … Sun=6 |
| `threshold` | `float` | Jackpot in pounds (e.g. `50_000_000.0`) |

### Required methods

| Method | Signature | Description |
|---|---|---|
| `fetch_jackpot` | `() -> float \| None` | Fetches XML, parses `next-estimated` value. Returns `None` on any failure. |
| `should_notify_today` | `() -> bool` | Returns `True` if today is the next working day after a draw day. Accounts for weekends (Friday draw → Monday notify). |

### XML endpoints

| Game | URL |
|---|---|
| Lotto | `https://www.national-lottery.co.uk/results/lotto/draw-history/xml` |
| EuroMillions | `https://www.national-lottery.co.uk/results/euromillions/draw-history/xml` |
| Set For Life | `https://www.national-lottery.co.uk/results/set-for-life/draw-history/xml` |
| Thunderball | `https://www.national-lottery.co.uk/results/thunderball/draw-history/xml` |

Requests include a `User-Agent` header to avoid 403 responses.

---

## BaseNotifier (ABC)

Each notifier subclass lives in `notifiers/`.

### Required method

```python
def send(self, results: list[tuple[str, float, float]]) -> None:
    """
    results: list of (game_name, jackpot, threshold) for all qualifying games today.
    """
```

### TelegramNotifier

Reads two env vars (injected as GitHub Actions secrets):
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Sends a single message batching all qualifying games:

```
🎰 High prizes today!
• EuroMillions: £95,000,000.00 (threshold: £50,000,000.00)
• Lotto: £12,500,000.00 (threshold: £10,000,000.00)
```

---

## main.py

```python
games = [Lotto(), EuroMillions(), SetForLife(), Thunderball()]
notifiers = [TelegramNotifier()]

qualifying = []
for game in games:
    if not game.should_notify_today():
        continue
    jackpot = game.fetch_jackpot()
    if jackpot is not None and jackpot >= game.threshold:
        qualifying.append((game.name, jackpot, game.threshold))

if qualifying:
    for notifier in notifiers:
        notifier.send(qualifying)
```

---

## GitHub Actions Workflow

**File:** `.github/workflows/notify.yml`  
**Schedule:** `cron: '0 9 * * 1-5'` — 9am UTC, Monday–Friday

**Required secrets:**
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

**Steps:**
1. Checkout repo
2. Setup Python
3. Install dependencies (`pip install -e .` or `pip install requests`)
4. Run `python main.py`

---

## Error Handling

| Failure | Behaviour |
|---|---|
| XML fetch failure (403, network error) | Log error, return `None`, skip game |
| XML parse failure (unexpected structure) | Log error, return `None`, skip game |
| Telegram send failure | Log error, don't crash — other notifiers still run |
| No games qualify today | Silent exit, no message sent |

Errors are printed to stdout (visible in GitHub Actions logs).

---

## Draw Days

| Game | Draw Days | Notification Days |
|---|---|---|
| Lotto | Wednesday, Saturday | Thursday, Monday |
| EuroMillions | Tuesday, Friday | Wednesday, Monday |
| Set For Life | Monday, Thursday | Tuesday, Friday |
| Thunderball | Tuesday, Wednesday, Friday, Saturday | Wednesday, Thursday, Monday, Monday* |

*Saturday draw → Monday notify (skips weekend).

> **Note:** Exact draw days should be verified against the National Lottery website when implementing each game class. The table above is approximate.

---

## Dependencies

- `requests` — HTTP + XML fetch
- `xml.etree.ElementTree` (stdlib) — XML parsing
- Python 3.11+

No browser dependency. No state persistence needed (notification logic is purely date-based).
