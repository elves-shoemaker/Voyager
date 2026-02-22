import os
import time
import threading
import requests
from voyager import Voyager

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
last_task = ""

def discord_notifier(voyager):
    global last_task
    while True:
        try:
            current_task = getattr(voyager, 'task', None)
            if current_task and current_task != last_task:
                if DISCORD_WEBHOOK_URL:
                    requests.post(DISCORD_WEBHOOK_URL, json={"content": f"[VOYAGER] New task: {current_task}"}, timeout=5)
                last_task = current_task
        except:
            pass
        time.sleep(30)

openai_api_key = os.getenv("OPENAI_API_KEY", "dummy-key")
openai_api_base = os.getenv("OPENAI_API_BASE", "http://localhost:1234/v1")

azure_login = {
    "client_id": os.getenv("AZURE_CLIENT_ID", ""),
    "redirect_url": "https://127.0.0.1/auth-response",
    "secret_value": os.getenv("AZURE_SECRET_VALUE", ""),
    "version": "fabric-loader-0.14.18-1.19",
} if os.getenv("AZURE_CLIENT_ID") else None

mc_host = os.getenv("MINECRAFT_HOST", "localhost")
mc_port = int(os.getenv("MINECRAFT_PORT", "25565"))
server_port = int(os.getenv("MINDSERVER_PORT", "3000"))

action_model = os.getenv("OPENAI_MODEL_NAME", "gpt-4")

voyager = Voyager(
    azure_login=azure_login,
    mc_host=mc_host,
    mc_port=mc_port if not azure_login else None,
    server_port=server_port,
    openai_api_key=openai_api_key,
    action_agent_model_name=action_model,
    curriculum_agent_model_name=action_model,
    critic_agent_model_name=action_model,
    skill_manager_model_name=action_model,
)

if DISCORD_WEBHOOK_URL:
    thread = threading.Thread(target=discord_notifier, args=(voyager,), daemon=True)
    thread.start()

voyager.learn()
