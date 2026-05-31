from games.base import Weekday
from notifiers.base import BaseNotifier


# Output format:
# ┌──────────────┬─────────────────┬────────────────┬──────────────────┬─────────────┐
# │ Game         │ Jackpot         │ Threshold      │ Notify Day       │ Must Be Won │
# ├──────────────┼─────────────────┼────────────────┼──────────────────┼─────────────┤
# │ EuroMillions │ £122,000,000.00 │ £75,000,000.00 │ Monday, Thursday │ —           │
# │ Lotto        │ £5,013,960.00   │ £5,000,000.00  │ Tuesday, Friday  │ N           │
# └──────────────┴─────────────────┴────────────────┴──────────────────┴─────────────┘
class ConsoleNotifier(BaseNotifier):
    def send(self, results):
        rows = []
        for game_name, jackpot, prize_threshold, draw_days, is_roll_down in results:
            notify_day = ", ".join(Weekday((d - 1) % 7).name.capitalize() for d in draw_days)
            jackpot_str = f"£{jackpot:,.2f}" if jackpot is not None else "N/A"
            roll_down_str = "Y" if is_roll_down is True else ("N" if is_roll_down is False else "—")
            rows.append((game_name, jackpot_str, f"£{prize_threshold:,.2f}", notify_day, roll_down_str))

        col_widths = (
            max(len("Game"), max(len(r[0]) for r in rows)),
            max(len("Jackpot"), max(len(r[1]) for r in rows)),
            max(len("Threshold"), max(len(r[2]) for r in rows)),
            max(len("Notify Day"), max(len(r[3]) for r in rows)),
            max(len("Must Be Won"), max(len(r[4]) for r in rows)),
        )

        def row(*cols, sep="│"):
            return " ".join(
                f"{sep} {c:<{col_widths[i]}}" for i, c in enumerate(cols)
            ) + f" {sep}"

        def divider(left, mid, right, fill="─"):
            return left + mid.join(fill * (w + 2) for w in col_widths) + right

        print("=== High Prize Alert ===")
        print(divider("┌", "┬", "┐"))
        print(row("Game", "Jackpot", "Threshold", "Notify Day", "Must Be Won"))
        print(divider("├", "┼", "┤"))
        for r in rows:
            print(row(*r))
        print(divider("└", "┴", "┘"))
