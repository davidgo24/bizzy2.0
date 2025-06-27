from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os

from bizzy_brain.core import message_router
from bizzy_brain.memory import owner_memory, client_memory
from bizzy_brain.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, OWNER_PHONE
from bizzy_brain.relay import responder
from bizzy_brain.chat import engine
from bizzy_brain.core.models import Message
from bizzy_brain.core.states import ConversationState

app = FastAPI()

# Initialize Twilio Client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.post("/sms")
async def sms_reply(request: Request):
    form_data = await request.form()
    incoming_msg = form_data.get("Body")
    sender_phone = form_data.get("From")
    
    resp = MessagingResponse()

    if sender_phone == OWNER_PHONE:
        # This is a message from the owner
        # We need to determine which client conversation this response is for
        # For simplicity in this MVP, we'll assume the owner's response is for the latest unresponded ticket
        # In a real app, you'd have a more robust way to link owner responses to client threads (e.g., a ticket ID in the owner notification)
        
        latest_unresponded_ticket = None
        # Iterate through all tickets to find the latest unresponded one
        # This is inefficient for many tickets, but works for MVP
        for filename in os.listdir(owner_memory.RELAY_TICKETS_DIR):
            if filename.startswith("relay_") and filename.endswith(".json"):
                ticket_id = filename[len("relay_"):-len(".json")]
                ticket = owner_memory.load_ticket(ticket_id)
                if ticket and not ticket.responded:
                    if latest_unresponded_ticket is None or ticket.timestamp > latest_unresponded_ticket.timestamp:
                        latest_unresponded_ticket = ticket
        
        if latest_unresponded_ticket:
            client_phone_for_owner_response = latest_unresponded_ticket.client_phone
            
            # Update the ticket as responded
            latest_unresponded_ticket.responded = True
            latest_unresponded_ticket.owner_response = incoming_msg # Store owner's actual response
            owner_memory.save_ticket(latest_unresponded_ticket)

            # Inject owner's response into the client's thread and get Bizzy's reply
            thread = client_memory.load_thread(client_phone_for_owner_response)
            thread.state = ConversationState.OWNER_RESPONDED # Update state after owner responds
            thread = responder.inject_owner_response(thread, incoming_msg)
            client_memory.save_thread(thread)

            # Bizzy now generates a response to the client based on the owner's input
            bizzy_response_to_client = engine.ask_bizzy(thread)
            thread.messages.append(Message(role="bizzy", content=bizzy_response_to_client))
            thread.state = ConversationState.GENERAL_INQUIRY # Transition back to general inquiry
            client_memory.save_thread(thread) # Save thread after Bizzy's response

            # Send Bizzy's response to the client
            twilio_client.messages.create(
                to=client_phone_for_owner_response,
                from_=TWILIO_PHONE_NUMBER,
                body=bizzy_response_to_client
            )
            resp.message("Owner response processed and sent to client.")
        else:
            resp.message("No active client intervention ticket found for your response.")
    else:
        # This is a message from a client
        bizzy_response, intervention_needed, thread = message_router.handle_incoming_message(sender_phone, incoming_msg)

        if intervention_needed:
            # Notify owner
            # Summarize conversation for owner
            summary = engine.summarize_conversation(thread)
            
            # Fetch the newly created ticket to get the reason for intervention
            current_intervention_ticket = owner_memory.get_latest_ticket(sender_phone)
            reason_for_intervention = current_intervention_ticket.reason_for_intervention if current_intervention_ticket else 'N/A'

            owner_notification_msg = f"Client {sender_phone} needs your input!\n\n--- Conversation Summary ---\n{summary}\n----------------------------\nReason: {reason_for_intervention}"
            
            twilio_client.messages.create(
                to=OWNER_PHONE,
                from_=TWILIO_PHONE_NUMBER,
                body=owner_notification_msg
            )
            resp.message("Melissa has been notified and will get back to you shortly.")
        elif bizzy_response:
            resp.message(bizzy_response)
        else:
            # Bizzy is silent (e.g., waiting for owner response to an existing ticket)
            resp.message("Thanks for your message! Melissa will get back to you shortly.") # Generic holding message

    return Response(content=str(resp), media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
