# bizzy-gemini-version-scaffold/tests/test_bizzy_flow.py

import pytest
import os
import shutil
from datetime import datetime, timedelta
from bizzy_brain.core import message_router
from bizzy_brain.memory import client_memory, owner_memory, archiver
from bizzy_brain.core.models import Message, Thread
from bizzy_brain.config import CLIENT_THREADS_DIR, RELAY_TICKETS_DIR, ARCHIVES_DIR
from bizzy_brain.relay import responder, followup_checker

# --- Fixtures for Test Setup/Teardown ---

@pytest.fixture(autouse=True)
def clean_data_dirs():
    # Setup: Ensure data directories are clean before each test
    for directory in [CLIENT_THREADS_DIR, RELAY_TICKETS_DIR, ARCHIVES_DIR]:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory, exist_ok=True)
    yield
    # Teardown: Clean up after each test (optional, but good for isolation)
    for directory in [CLIENT_THREADS_DIR, RELAY_TICKETS_DIR, ARCHIVES_DIR]:
        if os.path.exists(directory):
            shutil.rmtree(directory)

# --- Test Cases ---

def test_bizzy_responds_normally():
    phone = "+12223334444"
    message = "Hi Bizzy, what are your salon hours today?"

    message_router.handle_incoming_message(phone, message)

    thread = client_memory.load_thread(phone)
    assert len(thread.messages) == 2  # Client message + Bizzy's response
    assert thread.messages[0].role == "client"
    assert thread.messages[1].role == "bizzy"

def test_owner_intervention_flow():
    phone = "+12223334445"
    # Client message triggering intervention
    message_router.handle_incoming_message(phone, "I need to speak to a human ASAP!")

    thread = client_memory.load_thread(phone)
    assert len(thread.messages) == 1  # Only client message, Bizzy should be silent

    # Verify a ticket was created
    latest_ticket = owner_memory.get_latest_ticket(phone)
    assert latest_ticket is not None
    assert not latest_ticket.responded

    # Simulate owner response (as main.py would do)
    owner_response_text = "Melissa will call you shortly."
    thread = client_memory.load_thread(phone)
    thread = responder.inject_owner_response(thread, owner_response_text)
    client_memory.save_thread(thread)

    latest_ticket.responded = True
    owner_memory.save_ticket(latest_ticket)

    thread = client_memory.load_thread(phone)
    assert len(thread.messages) == 2  # Client message + Owner's injected message
    assert thread.messages[1].role == "bizzy"
    assert "Melissa says:" in thread.messages[1].content

    # Client sends another message
    message_router.handle_incoming_message(phone, "Okay, thanks!")

    thread = client_memory.load_thread(phone)
    # Check if Bizzy followed up based on GPT's decision
    if followup_checker.needs_followup(thread):
        assert len(thread.messages) == 4  # Client message + Owner response + Client message + Bizzy follow-up
        assert thread.messages[3].role == "bizzy"
    else:
        assert len(thread.messages) == 3  # Client message + Owner response + Client message
        assert thread.messages[2].role == "client"


def test_archiving_stale_threads():
    phone = "+12223334446"
    message = "Test message for archiving."

    # Create a thread and make it stale (by modifying its file's timestamp)
    message_router.handle_incoming_message(phone, message)
    thread_path = client_memory.get_thread_path(phone)

    # Set modification time to be very old
    old_time = (datetime.now() - timedelta(days=30)).timestamp()
    os.utime(thread_path, (old_time, old_time))

    # Run archiver
    archiver.archive_stale_threads(days_stale=7)

    # Verify thread is moved to archive
    assert not os.path.exists(thread_path)
    assert os.path.exists(os.path.join(ARCHIVES_DIR, os.path.basename(thread_path)))
