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

    latest_ticket = owner_memory.get_latest_ticket(phone)

    if latest_ticket and not latest_ticket.responded:
        # Case 1: There's an existing unresponded ticket. Bizzy remains silent.
        intervention_needed = True
    else:
        # Case 2: No unresponded ticket, or the latest one has been responded to.
        # Now, decide if Bizzy should respond, follow up, or trigger a new intervention.
        intervention_flag, reason = relay_controller.needs_owner_intervention(thread)

        if intervention_flag:
            owner_memory.create_ticket(phone, reason_for_intervention=reason) # Create a new ticket for this new intervention
            thread.state = ConversationState.AWAITING_OWNER_RESPONSE
            intervention_needed = True
        elif followup_checker.needs_followup(thread):
            # No intervention needed, but Bizzy needs to follow up.
            bizzy_response = engine.ask_bizzy(thread)
            thread.messages.append(Message(role="bizzy", content=bizzy_response))
            thread.state = ConversationState.GENERAL_INQUIRY # Transition to a general state
        else:
            # No intervention, no specific follow-up, Bizzy responds normally.
            bizzy_response = engine.ask_bizzy(thread)
            thread.messages.append(Message(role="bizzy", content=bizzy_response))
            thread.state = ConversationState.GENERAL_INQUIRY # Transition to a general state

    client_memory.save_thread(thread)
    return bizzy_response, intervention_needed, thread
