# bizzy-gemini-version-scaffold/bizzy_brain/core/message_router.py

from ..memory import client_memory, owner_memory
from .models import Message, Thread
from ..relay import relay_controller, followup_checker
from ..chat import engine
from .states import ConversationState

def handle_incoming_message(phone: str, message: str) -> tuple[str | None, bool, Thread]:
    """Main entry point for handling a new message."""
    thread = client_memory.load_thread(phone)
    thread.messages.append(Message(role="client", content=message))

    latest_ticket = owner_memory.get_latest_ticket(phone)

    bizzy_response = None
    intervention_needed = False

    # Determine the current state and transition
    current_state = thread.state

    if thread.state == ConversationState.AWAITING_OWNER_RESPONSE:
        # Case 1: Bizzy is awaiting owner response. Remain silent.
        intervention_needed = True
    elif relay_controller.needs_owner_intervention(thread)[0]:
        # Case 2: A new intervention is needed. Create ticket, set state, remain silent.
        intervention_needed_flag, reason = relay_controller.needs_owner_intervention(thread)
        owner_memory.create_ticket(phone, reason_for_intervention=reason)
        thread.state = ConversationState.AWAITING_OWNER_RESPONSE
        intervention_needed = True
    elif followup_checker.needs_followup(thread):
        # Case 3: No pending intervention, but Bizzy needs to follow up.
        bizzy_response = engine.ask_bizzy(thread)
        thread.messages.append(Message(role="bizzy", content=bizzy_response))
        thread.state = ConversationState.GENERAL_INQUIRY # Transition to a general state
    else:
        # Case 4: No intervention, no specific follow-up, Bizzy responds normally.
        bizzy_response = engine.ask_bizzy(thread)
        thread.messages.append(Message(role="bizzy", content=bizzy_response))
        thread.state = ConversationState.GENERAL_INQUIRY # Transition to a general state

    client_memory.save_thread(thread)
    return bizzy_response, intervention_needed, thread
