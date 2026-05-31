from games.base import Weekday
from notifiers.base import BaseNotifier


class ConsoleNotifier(BaseNotifier):
    def send(self, results):
        rows = [
            (
                game_name,
                f"£{jackpot:,.2f}",
                f"£{prize_threshold:,.2f}",
                ", ".join(Weekday((d - 1) % 7).name.capitalize() for d in draw_days),
            )
            for game_name, jackpot, prize_threshold, draw_days in results
        ]

        col_widths = (
            max(len("Game"), max(len(r[0]) for r in rows)),
            max(len("Jackpot"), max(len(r[1]) for r in rows)),
            max(len("Threshold"), max(len(r[2]) for r in rows)),
            max(len("Notify Day"), max(len(r[3]) for r in rows)),
        )

        def row(a, b, c, d, sep="│"):
            return (
                f"{sep} {a:<{col_widths[0]}} {sep} {b:<{col_widths[1]}} "
                f"{sep} {c:<{col_widths[2]}} {sep} {d:<{col_widths[3]}} {sep}"
            )

        def divider(left, mid, right, fill="─"):
            return (
                left + fill * (col_widths[0] + 2) + mid
                + fill * (col_widths[1] + 2) + mid
                + fill * (col_widths[2] + 2) + mid
                + fill * (col_widths[3] + 2) + right
            )

        print("=== High Prize Alert ===")
        print(divider("┌", "┬", "┐"))
        print(row("Game", "Jackpot", "Threshold", "Notify Day"))
        print(divider("├", "┼", "┤"))
        for r in rows:
            print(row(*r))
        print(divider("└", "┴", "┘"))
