# national-lottery-high-prize-notifier
Notifying users when The National Lottery games reach a decent prize

## Schedule

The notifier runs automatically every day at midnight UTC via GitHub Actions. It can also be triggered manually from the Actions tab at any time.

## Games

| Game | Draw Days | Prize Threshold |
|------|-----------|-----------------|
| EuroMillions | Tuesday, Friday | £75,000,000 |

## How to Run Locally

Install dependencies:

```bash
pip install -e .
```

Run in test mode — skips the day check and prints results to the console regardless of draw schedule:

```bash
python main.py --test
```
