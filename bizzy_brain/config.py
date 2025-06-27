# bizzy-gemini-version-scaffold/bizzy_brain/config.py
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# --- Core Paths ---
# Use an absolute path to ensure robustness, regardless of where the script is run.
BIZZY_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BIZZY_ROOT, "data")
CLIENT_THREADS_DIR = os.path.join(DATA_DIR, "client_threads")
RELAY_TICKETS_DIR = os.path.join(DATA_DIR, "relay_tickets")
ARCHIVES_DIR = os.path.join(DATA_DIR, "archives")

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Now loaded from .env

# --- Twilio Credentials ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER") # Your Twilio phone number (e.g., +1234567890)

# --- Phone Numbers ---
OWNER_PHONE = os.getenv("OWNER_PHONE") # Your actual phone number (e.g., +1987654321)
BIZZY_PHONE = TWILIO_PHONE_NUMBER # Bizzy's phone number is your Twilio number
