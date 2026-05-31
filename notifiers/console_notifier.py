from notifiers.base import BaseNotifier


class ConsoleNotifier(BaseNotifier):
    def send(self, results):
        col_widths = (
            max(len("Game"), max(len(g) for g, _, _ in results)),
            max(len("Jackpot"), max(len(f"£{j:,.2f}") for _, j, _ in results)),
            max(len("Threshold"), max(len(f"£{t:,.2f}") for _, _, t in results)),
        )

        def row(a, b, c, sep="│"):
            return f"{sep} {a:<{col_widths[0]}} {sep} {b:<{col_widths[1]}} {sep} {c:<{col_widths[2]}} {sep}"

        def divider(left, mid, right, fill="─"):
            return left + fill * (col_widths[0] + 2) + mid + fill * (col_widths[1] + 2) + mid + fill * (col_widths[2] + 2) + right

        print("=== High Prize Alert ===")
        print(divider("┌", "┬", "┐"))
        print(row("Game", "Jackpot", "Threshold"))
        print(divider("├", "┼", "┤"))
        for game_name, jackpot, prize_threshold in results:
            print(row(game_name, f"£{jackpot:,.2f}", f"£{prize_threshold:,.2f}"))
        print(divider("└", "┴", "┘"))
