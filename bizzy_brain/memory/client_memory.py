# bizzy-gemini-version-scaffold/bizzy_brain/memory/client_memory.py

import json
import os
from ..core.models import Thread, Message
from ..core.states import ConversationState
from ..config import CLIENT_THREADS_DIR
from ..utils.json_encoder import EnhancedJSONEncoder

def get_thread_path(client_phone: str) -> str:
    # Ensure the directory exists
    os.makedirs(CLIENT_THREADS_DIR, exist_ok=True)
    return os.path.join(CLIENT_THREADS_DIR, f"{client_phone}.json")

def load_thread(client_phone: str) -> Thread:
    thread_path = get_thread_path(client_phone)
    try:
        with open(thread_path, 'r') as f:
            data = json.load(f)
            messages = [Message(**msg) for msg in data.get('messages', [])]
            state = ConversationState(data.get('state', ConversationState.INITIAL.value))
            return Thread(client_phone=data['client_phone'], messages=messages, state=state)
    except (FileNotFoundError, json.JSONDecodeError):
        return Thread(client_phone=client_phone)

def save_thread(thread: Thread):
    thread_path = get_thread_path(thread.client_phone)
    with open(thread_path, 'w') as f:
        json.dump(thread, f, indent=4, cls=EnhancedJSONEncoder)
