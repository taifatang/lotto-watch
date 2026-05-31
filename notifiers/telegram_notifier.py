import os
import requests

from notifiers.base import BaseNotifier

# Output format:
# 🎰 [Tomorrow] Big Jackpot Alert!
# 🌟 EuroMillions: £122M
# 🎱 Lotto: £20M (Must-be-won draw)


class TelegramNotifier(BaseNotifier):
    _api_url = "https://api.telegram.org/bot{token}/sendMessage"

    def send(self, results):
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")

        if not token or not chat_id:
            print("Telegram skipped: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set.")
            return

        lines = ["🎰 [Tomorrow] Big Jackpot Alert!"]
        for game_name, jackpot, prize_threshold, draw_days, is_roll_down in results:
            jackpot_str = f"£{round(jackpot / 1_000_000)}M" if jackpot is not None else "N/A"
            suffix = " (Must-be-won draw)" if is_roll_down else ""
            lines.append(f"{game_name}: {jackpot_str}{suffix}")

        try:
            response = requests.post(
                self._api_url.format(token=token),
                json={"chat_id": chat_id, "text": "\n".join(lines)},
                timeout=10,
            )
            response.raise_for_status()
            print("Telegram notification sent.")
        except Exception as e:
            print(f"Telegram send failed: {e}")
