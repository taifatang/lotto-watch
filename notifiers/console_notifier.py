from games.base import Weekday
from notifiers.base import BaseNotifier


class ConsoleNotifier(BaseNotifier):
    def send(self, results):
        rows = []
        for game_name, jackpot, prize_threshold, draw_days, rollover_count, max_rollovers in results:
            notify_day = ", ".join(Weekday((d - 1) % 7).name.capitalize() for d in draw_days)
            jackpot_str = f"£{jackpot:,.2f}" if jackpot is not None else "N/A"
            rollover_str = (
                f"{rollover_count}/{max_rollovers}" if rollover_count is not None and max_rollovers is not None
                else str(rollover_count) if rollover_count is not None
                else "—"
            )
            rows.append((game_name, jackpot_str, f"£{prize_threshold:,.2f}", notify_day, rollover_str))

        col_widths = (
            max(len("Game"), max(len(r[0]) for r in rows)),
            max(len("Jackpot"), max(len(r[1]) for r in rows)),
            max(len("Threshold"), max(len(r[2]) for r in rows)),
            max(len("Notify Day"), max(len(r[3]) for r in rows)),
            max(len("Rollovers"), max(len(r[4]) for r in rows)),
        )

        def row(*cols, sep="│"):
            return " ".join(
                f"{sep} {c:<{col_widths[i]}}" for i, c in enumerate(cols)
            ) + f" {sep}"

        def divider(left, mid, right, fill="─"):
            return left + mid.join(fill * (w + 2) for w in col_widths) + right

        print("=== High Prize Alert ===")
        print(divider("┌", "┬", "┐"))
        print(row("Game", "Jackpot", "Threshold", "Notify Day", "Rollovers"))
        print(divider("├", "┼", "┤"))
        for r in rows:
            print(row(*r))
        print(divider("└", "┴", "┘"))
