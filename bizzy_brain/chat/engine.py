import openai
from bizzy_brain.config import OPENAI_API_KEY
from bizzy_brain.chat.prompt_templates import DEFAULT_PROMPT, SUMMARY_PROMPT
from bizzy_brain.memory import owner_memory

openai.api_key = OPENAI_API_KEY

def _map_role_to_openai(role: str) -> str:
    if role == "client":
        return "user"
    elif role == "bizzy":
        return "assistant"
    elif role == "owner":
        return "user" # Owner messages are also user input from the AI's perspective
    return role # Return as is if it's already an OpenAI role

def ask_bizzy(thread):
    print("\n🤖 Bizzy is thinking...")

    messages = [{'role': 'system', 'content': DEFAULT_PROMPT}]

    # Inject reason for intervention if available
    latest_ticket = owner_memory.get_latest_ticket(thread.client_phone)
    if latest_ticket and latest_ticket.reason_for_intervention:
        messages.append({'role': 'system', 'content': f"The owner was brought into this conversation because: {latest_ticket.reason_for_intervention}. Integrate this context into your response."})

    for msg in thread.messages:
        messages.append({'role': _map_role_to_openai(msg.role), 'content': msg.content})

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Or another suitable model like "gpt-3.5-turbo"
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content
    except openai.APIError as e:
        print(f"OpenAI API Error: {e}")
        return "I'm sorry, I'm having trouble connecting to my brain right now. Please try again later."

def summarize_conversation(thread) -> str:
    print("\n🧠 Bizzy is summarizing the conversation...")

    messages_for_openai = []
    for msg in thread.messages:
        messages_for_openai.append({'role': _map_role_to_openai(msg.role), 'content': msg.content})

    messages = [
        {'role': 'system', 'content': SUMMARY_PROMPT},
    ] + messages_for_openai + [
        {'role': 'user', 'content': "Provide a concise summary of this conversation for the salon owner."}
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.0,
            max_tokens=100
        )
        return response.choices[0].message.content
    except openai.APIError as e:
        print(f"OpenAI API Error during summarization: {e}")
        return "Unable to summarize conversation due to API error."
