import os
import requests

from notifiers.base import BaseNotifier

# Output format:
# 🎰 High Prize Alert!
# • EuroMillions: £122,000,000.00
# • Lotto: £5,013,960.00
#   ⚠️ Must-be-won draw!


class TelegramNotifier(BaseNotifier):
    _api_url = "https://api.telegram.org/bot{token}/sendMessage"

    def send(self, results):
        token = os.environ["TELEGRAM_BOT_TOKEN"]
        chat_id = os.environ["TELEGRAM_CHAT_ID"]

        lines = ["🎰 High Prize Alert!"]
        for game_name, jackpot, prize_threshold, draw_days, is_roll_down in results:
            jackpot_str = f"£{jackpot:,.2f}" if jackpot is not None else "N/A"
            lines.append(f"• {game_name}: {jackpot_str}")
            if is_roll_down:
                lines.append("  ⚠️ Must-be-won draw!")

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
