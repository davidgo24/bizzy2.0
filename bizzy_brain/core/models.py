from dataclasses import dataclass, field
from typing import List
import datetime
from bizzy_brain.core.states import ConversationState

@dataclass
class Message:
    role: str  # "client", "bizzy", "owner"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())

@dataclass
class Thread:
    client_phone: str
    messages: List[Message] = field(default_factory=list)
    state: ConversationState = ConversationState.INITIAL

@dataclass
class Ticket:
    ticket_id: str
    client_phone: str
    timestamp: str
    responded: bool = False
    owner_response: str = ""
    reason_for_intervention: str | None = None
