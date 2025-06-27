# bizzy-gemini-version-scaffold/main.py

import click
from bizzy_brain.core import message_router
from bizzy_brain.memory import client_memory, owner_memory, archiver
from bizzy_brain.relay import responder
from bizzy_brain.chat import engine
from bizzy_brain.core.models import Message
from bizzy_brain.core.states import ConversationState

@click.group()
def cli():
    """Bizzy AI SMS Assistant Simulation"""
    pass

@cli.command()
@click.argument('phone')
@click.argument('message')
def send(phone, message):
    """Simulates a client sending a message."""
    print(f"\n📱 New message from {phone}: '{message}'")
    message_router.handle_incoming_message(phone, message)

@cli.command()
@click.argument('client_phone')
@click.argument('owner_response')
def respond(client_phone, owner_response):
    """Allows the owner to respond to a client's request."""
    latest_ticket = owner_memory.get_latest_ticket(client_phone)
    if latest_ticket:
        latest_ticket.responded = True
        latest_ticket.owner_response = owner_response # Save the owner's response
        owner_memory.save_ticket(latest_ticket)
    else:
        print("\n⚠️ No ticket found for this client to respond to.")

    thread = client_memory.load_thread(client_phone)
    thread.state = ConversationState.OWNER_RESPONDED # Update state after owner responds
    thread = responder.inject_owner_response(thread, owner_response)
    client_memory.save_thread(thread)
    print("\n✅ Owner response injected into the conversation.")

@cli.command()
@click.option('--days', default=7, help='Number of days after which a thread is considered stale.')
def archive(days):
    """Archives stale client conversation threads."""
    archiver.archive_stale_threads(days)

@cli.command()
@click.argument('phone')
def chat(phone):
    """Starts an interactive chat simulation with a client."""
    print(f"\n--- Starting interactive chat with {phone} ---")
    print("Type 'exit' to end the chat.")

    while True:
        client_message = input("\nClient: ")
        if client_message.lower() == 'exit':
            break

        bizzy_response, intervention_needed, thread = message_router.handle_incoming_message(phone, client_message)

        if intervention_needed:
            print(f"\n🚨 Owner intervention needed for {phone}!")
            print("--- Conversation History ---")
            for msg in thread.messages:
                print(f"{msg.role.capitalize()}: {msg.content}")
            print("----------------------------")
            owner_response = input("Owner (your) response: ")
            
            latest_ticket = owner_memory.get_latest_ticket(phone)
            if latest_ticket:
                latest_ticket.responded = True
                owner_memory.save_ticket(latest_ticket)
            else:
                print("\n⚠️ No ticket found for this client to respond to.")

            thread = client_memory.load_thread(phone)
            thread.state = ConversationState.OWNER_RESPONDED # Update state after owner responds
            thread = responder.inject_owner_response(thread, owner_response)
            client_memory.save_thread(thread)
            print("\n✅ Owner response injected into the conversation.")

            # Bizzy now generates a response to the client based on the owner's input
            bizzy_response_to_client = engine.ask_bizzy(thread)
            thread.messages.append(Message(role="bizzy", content=bizzy_response_to_client))
            thread.state = ConversationState.GENERAL_INQUIRY # Transition back to general inquiry
            client_memory.save_thread(thread) # Save thread after Bizzy's response
            print(f"\n🤖 Bizzy replies to {phone}: {bizzy_response_to_client}")
        elif bizzy_response:
            print(f"\n🤖 Bizzy replies to {phone}: {bizzy_response}")
        else:
            print(f"\nBizzy is silent (waiting for owner or no follow-up needed).")

    print("\n--- Chat ended ---")

if __name__ == "__main__":
    cli()
