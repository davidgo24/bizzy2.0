# bizzy-gemini-version-scaffold/bizzy_brain/relay/responder.py

from bizzy_brain.core.models import Thread, Message

def inject_owner_response(thread: Thread, owner_response: str) -> Thread:
    """Injects the owner's response into the conversation thread."""
    response_message = Message(role="owner", content=owner_response)
    thread.messages.append(response_message)
    return thread
