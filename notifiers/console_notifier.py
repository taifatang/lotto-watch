from notifiers.base import BaseNotifier


class ConsoleNotifier(BaseNotifier):
    def send(self, results):
        col_widths = (
            max(len("Game"), max(len(g) for g, _, _, _ in results)),
            max(len("Jackpot"), max(len(f"£{j:,.2f}") for _, j, _, _ in results)),
            max(len("Threshold"), max(len(f"£{t:,.2f}") for _, _, t, _ in results)),
            max(len("Notify Day"), max(len(d) for _, _, _, d in results)),
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
        for game_name, jackpot, prize_threshold, notify_days in results:
            print(row(game_name, f"£{jackpot:,.2f}", f"£{prize_threshold:,.2f}", notify_days))
        print(divider("└", "┴", "┘"))
