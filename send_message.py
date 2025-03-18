import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
RECIPIENT_WAID = "919500646732"  # Example: Indian number format
  # Replace with your own WhatsApp number

def send_test_message():
    """Sends a test message to your WhatsApp using the WhatsApp Cloud API."""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT_WAID,
        "type": "text",
        "text": {"body": "Hello! This is a test message from my AI Tutor."}
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.json())

# Run the function
if __name__ == "__main__":
    send_test_message()
