# bizzy-gemini-version-scaffold/bizzy_brain/core/states.py

from enum import Enum

class ConversationState(Enum):
    INITIAL = "initial" # Starting state of a new conversation
    GENERAL_INQUIRY = "general_inquiry" # Client asking general questions
    BOOKING_IN_PROGRESS = "booking_in_progress" # Client is trying to book an appointment
    EMERGENCY_HANDLING = "emergency_handling" # Client has a hair emergency
    AWAITING_OWNER_RESPONSE = "awaiting_owner_response" # Bizzy is waiting for owner input
    OWNER_RESPONDED = "owner_responded" # Owner has responded, Bizzy can follow up
    CONVERSATION_CLOSED = "conversation_closed" # Conversation is resolved or ended
