# LottoWatch

Only worth playing the lottery when the jackpot is massive. LottoWatch reminds you after work when a prize is worth going for — so you don't miss out.

Join the Telegram channel: https://t.me/lottowatch

<img src="assets/images/telegram_notifier_example.jpg" width="350" alt="LottoWatch Telegram notification example" />

## Schedule

Runs Monday to Thursday at 5pm UTC.

## Games

| Game | Draw Days | Average | Median | Historic Highest | Notifying Condition |
|------|-----------|---------|--------|------------------|---------------------|
| EuroMillions | Tuesday, Friday | £69M | £62M | £195M | <ul><li>Jackpot ≥ £75,000,000</li></ul> |
| Lotto | Wednesday, Saturday | TBC | TBC | £66M | <ul><li>Jackpot ≥ £5,000,000</li><li>Must-be-won draw</li></ul> |

*Average and median based on last 52 draws (180 days) as of 31 May 2026.*

## Notifiers

| Name | When | Output |
|------|------|--------|
| Console | `--test` mode | Prints a table to stdout |
| Telegram | Scheduled runs | Sends a message to the channel |

## How to Run Locally

Install dependencies:

```bash
pip install -e .
```

Run in test mode — skips the day check and prints to console:

```bash
python main.py --test
```
