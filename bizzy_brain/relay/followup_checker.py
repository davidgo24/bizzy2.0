import openai
from bizzy_brain.config import OPENAI_API_KEY
from bizzy_brain.core.models import Thread

openai.api_key = OPENAI_API_KEY

FOLLOWUP_PROMPT = """You are an AI assistant helping to manage conversations for Melissa's hair salon.
Review the following conversation history. The last message is from the owner (Melissa).
Determine if a follow-up message from Bizzy (the AI) is needed to keep the conversation flowing or to provide further assistance.

Consider the following:
- If the client's last message is a simple acknowledgment (e.g., "thanks", "ok"), a confirmation, or does not require a direct response, then NO follow-up is needed.
- If the client asks a new question, provides new information that requires a response, or indicates a need for further action, then YES a follow-up is needed.
- IMPORTANT: If the client's last message indicates a new emergency, distress, urgency, or a clear need for owner intervention (e.g., "help", "emergency", "messed up", "ASAP"), then NO follow-up is needed from Bizzy. This is to ensure the owner intervention logic is triggered instead.
- If the client's message is a direct answer to a question Bizzy just asked, and no further action is immediately required from Bizzy, then NO follow-up is needed.

Respond with ONLY 'YES' if a follow-up is needed, and 'NO' if it is not.

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

def needs_followup(thread: Thread) -> bool:
    print("\n🧠 Bizzy is checking if a follow-up is needed...")

    messages_for_openai = []
    for msg in thread.messages:
        messages_for_openai.append({'role': _map_role_to_openai(msg.role), 'content': msg.content})

    messages = [
        {'role': 'system', 'content': FOLLOWUP_PROMPT},
    ] + messages_for_openai + [
        {'role': 'user', 'content': "Is a follow-up needed? Respond with ONLY 'YES' or 'NO'."}
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Or another suitable model
            messages=messages,
            temperature=0.0,
            max_tokens=5
        )
        decision = response.choices[0].message.content.strip().upper()

        if decision == "YES":
            print("\n💡 Follow-up needed (GPT-determined).")
            return True
        else:
            print("\n❌ No follow-up needed (GPT-determined).")
            return False
    except openai.APIError as e:
        print(f"OpenAI API Error during follow-up check: {e}")
        # Fallback to a safe default if API fails
        return False
