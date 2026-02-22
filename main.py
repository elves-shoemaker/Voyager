import os
import time
import threading
import requests
from voyager import Voyager

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
last_task = ""
last_action = ""
last_decision = ""
last_iter = -1

def discord_notifier(voyager):
    global last_task, last_action, last_decision, last_iter
    while True:
        try:
            current_task = getattr(voyager, 'task', None)
            current_iter = getattr(voyager, 'action_agent_rollout_num_iter', -1)
            conversations = getattr(voyager, 'conversations', [])
            
            if current_task and current_task != last_task:
                if DISCORD_WEBHOOK_URL:
                    requests.post(DISCORD_WEBHOOK_URL, json={"content": f"[VOYAGER] New task: {current_task}"}, timeout=5)
                last_task = current_task
            
            if conversations and current_iter != last_iter:
                last_conv = conversations[-1]
                if len(last_conv) >= 3:
                    _, _, ai_message = last_conv
                    if ai_message and ai_message != last_decision:
                        if DISCORD_WEBHOOK_URL:
                            requests.post(DISCORD_WEBHOOK_URL, json={"content": f"[VOYAGER] Decision:\n{ai_message[:500]}"}, timeout=5)
                        last_decision = ai_message
                    
                    code_pattern = "```javascript"
                    if code_pattern in ai_message:
                        code_start = ai_message.find(code_pattern) + len(code_pattern)
                        code_end = ai_message.find("```", code_start)
                        if code_end > code_start:
                            action_code = ai_message[code_start:code_end].strip()
                            if action_code and action_code != last_action:
                                if DISCORD_WEBHOOK_URL:
                                    requests.post(DISCORD_WEBHOOK_URL, json={"content": f"[VOYAGER] Action:\n{action_code[:500]}"}, timeout=5)
                                last_action = action_code
                
                last_iter = current_iter
                
        except Exception as e:
            print(f"Discord notifier error: {e}")
        time.sleep(5)

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
    resume=False,
)

if DISCORD_WEBHOOK_URL:
    thread = threading.Thread(target=discord_notifier, args=(voyager,), daemon=True)
    thread.start()

voyager.learn()
