# bizzy-gemini-version-scaffold/bizzy_brain/relay/relay_controller.py

import openai
from bizzy_brain.config import OPENAI_API_KEY
from bizzy_brain.core.models import Thread

openai.api_key = OPENAI_API_KEY

INTERVENTION_PROMPT = """You are an AI assistant whose sole purpose is to determine if a human (owner) needs to intervene in a conversation.
Review the following conversation between a client and Bizzy (an AI assistant for a hair salon).
Based on the client's last message and the overall context, decide if the owner needs to be alerted to take over the conversation.

Owner intervention is ABSOLUTELY REQUIRED if:
- The client explicitly asks for a human, manager, or to speak to Melissa directly.
- The client expresses any form of distress, emergency, or urgency (e.g., "ASAP", "emergency", "help me", "ruined my hair", "crisis", "messed up").
- The client asks a question that requires personalized advice, complex scheduling, or specific pricing that Bizzy cannot handle.
- The client expresses frustration, anger, or dissatisfaction.

Respond with ONLY 'YES' if owner intervention is needed, and 'NO' if it is not.

Conversation History:
"""

REASON_PROMPT = """You are an AI assistant. Given the following conversation, identify the primary reason why owner intervention is needed.
Be concise and provide a brief summary of the client's need or the situation.
Examples:
- "Client has a hair emergency."
- "Client wants to speak to Melissa directly."
- "Client needs complex scheduling."
- "Client is frustrated."

Conversation History:
"""

def _map_role_to_openai(role: str) -> str:
    if role == "client":
        return "user"
    elif role == "bizzy":
        return "assistant"
    elif role == "owner":
        return "user" # Owner messages are also user input from the AI's perspective
    return role # Return as is if it's already an OpenAI role

def needs_owner_intervention(thread: Thread) -> tuple[bool, str | None]:
    print("\n🧠 Bizzy is checking for owner intervention...")

    messages_for_openai = []
    for msg in thread.messages:
        messages_for_openai.append({'role': _map_role_to_openai(msg.role), 'content': msg.content})

    # Add the system prompt for intervention
    messages = [
        {'role': 'system', 'content': INTERVENTION_PROMPT},
    ] + messages_for_openai + [
        {'role': 'user', 'content': "Does the owner need to intervene? Respond with ONLY 'YES' or 'NO'."}
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Or another suitable model
            messages=messages,
            temperature=0.0, # Keep temperature low for deterministic output
            max_tokens=5
        )
        decision = response.choices[0].message.content.strip().upper()

        if decision == "YES":
            print("\n🚨 Owner intervention needed (GPT-determined)!")
            # Now, ask GPT for the reason
            reason_messages = [
                {'role': 'system', 'content': REASON_PROMPT},
            ] + messages_for_openai + [
                {'role': 'user', 'content': "What is the primary reason for owner intervention? Be concise."}
            ]
            reason_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=reason_messages,
                temperature=0.0,
                max_tokens=50
            )
            reason = reason_response.choices[0].message.content.strip()
            return True, reason
        else:
            print("\n✅ No owner intervention needed (GPT-determined).")
            return False, None
    except openai.APIError as e:
        print(f"OpenAI API Error during intervention check: {e}")
        # Fallback to a safe default if API fails
        return False, None
