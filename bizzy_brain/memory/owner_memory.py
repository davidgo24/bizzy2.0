# bizzy-gemini-version-scaffold/bizzy_brain/memory/owner_memory.py

import json
import os
import uuid
from datetime import datetime
from ..core.models import Ticket
from ..config import RELAY_TICKETS_DIR
from ..utils.json_encoder import EnhancedJSONEncoder

def create_ticket(client_phone: str, reason_for_intervention: str | None = None) -> Ticket:
    ticket_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    ticket = Ticket(ticket_id=ticket_id, client_phone=client_phone, timestamp=timestamp, reason_for_intervention=reason_for_intervention)
    save_ticket(ticket)
    return ticket

def get_ticket_path(ticket_id: str) -> str:
    # Ensure the directory exists
    os.makedirs(RELAY_TICKETS_DIR, exist_ok=True)
    return os.path.join(RELAY_TICKETS_DIR, f"relay_{ticket_id}.json")

def save_ticket(ticket: Ticket):
    ticket_path = get_ticket_path(ticket.ticket_id)
    print(f"\nDEBUG: Saving ticket {ticket.ticket_id} with responded={ticket.responded}")
    with open(ticket_path, 'w') as f:
        json.dump(ticket, f, indent=4, cls=EnhancedJSONEncoder)

def load_ticket(ticket_id: str) -> Ticket:
    ticket_path = get_ticket_path(ticket_id)
    try:
        with open(ticket_path, 'r') as f:
            data = json.load(f)
            return Ticket(**data)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def get_latest_ticket(client_phone: str) -> Ticket | None:
    os.makedirs(RELAY_TICKETS_DIR, exist_ok=True)
    latest_ticket = None
    latest_timestamp = None

    print(f"\nDEBUG: Searching for latest ticket for {client_phone}")
    for filename in os.listdir(RELAY_TICKETS_DIR):
        if filename.startswith("relay_") and filename.endswith(".json"):
            ticket_id = filename[len("relay_"):-len(".json")]
            ticket = load_ticket(ticket_id)
            if ticket and ticket.client_phone == client_phone:
                print(f"DEBUG: Found ticket {ticket.ticket_id} (responded={ticket.responded})")
                # Compare timestamps to find the latest ticket
                ticket_timestamp = datetime.fromisoformat(ticket.timestamp)
                if latest_ticket is None or ticket_timestamp > latest_timestamp:
                    latest_ticket = ticket
                    latest_timestamp = ticket_timestamp
    print(f"DEBUG: Latest ticket found: {latest_ticket.ticket_id if latest_ticket else 'None'}")
    return latest_ticket

def get_active_ticket(client_phone: str) -> Ticket | None:
    # Ensure the directory exists
    os.makedirs(RELAY_TICKETS_DIR, exist_ok=True)
    for filename in os.listdir(RELAY_TICKETS_DIR):
        if filename.startswith("relay_") and filename.endswith(".json"):
            ticket_id = filename[len("relay_"):-len(".json")]
            ticket = load_ticket(ticket_id)
            if ticket and ticket.client_phone == client_phone and not ticket.responded:
                return ticket
    return None
