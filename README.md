# national-lottery-high-prize-notifier
Notifying users when The National Lottery games reach a decent prize

## Games

| Game | Draw Days | Prize Threshold |
|------|-----------|-----------------|
| EuroMillions | Tuesday, Friday | £75,000,000 |

## How to Run

Install dependencies:

```bash
pip install requests
```

Run normally — only notifies on the day before a draw if the jackpot exceeds the threshold:

```bash
python main.py
```

Run in test mode — skips the day check and prints results to the console regardless of draw schedule:

```bash
python main.py --test
```

## Schedule

The notifier runs automatically every day at midnight UTC via GitHub Actions. It can also be triggered manually from the Actions tab at any time.
