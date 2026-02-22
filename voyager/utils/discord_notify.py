import os
import requests


def send_discord_notification(message: str):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return
    try:
        requests.post(
            "http://127.0.0.1:3000/step",
            json={"discord_message": message},
            timeout=5,
        )
    except Exception as e:
        print(f"[Discord] Failed to send: {e}")
