import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

# Load API keys from environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

def generate_ai_response(user_message):
    """Sends a request to OpenRouter API and returns the AI-generated response."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mistral-7b-instruct:free",  # Change model if needed
        "messages": [
            {"role": "system", "content": "You are an AI tutor helping students with educational topics."},
            {"role": "user", "content": user_message}
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.json()}"

def send_whatsapp_message(recipient, message):
    """Sends AI response back to the user via WhatsApp."""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        #"text": {"body": message}
        "text": {"body": f"🤖 AI Tutor:\n{message}"}
    }

    response = requests.post(url, json=payload, headers=headers)
    print("🔍 WhatsApp API Response:", response.json())  # Debugging line
    return response.json()

def send_template_message(recipient):
    """Sends a WhatsApp template message (required for first-time users)."""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "template",
        "template": {
            "name": "i am bot, how can i help you",  # Use an approved template name
            "language": {"code": "en_US"}
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    print("🔍 WhatsApp Template Response:", response.json())  # Debugging line
    return response.json()

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    """Handles incoming WhatsApp messages and sends AI responses."""
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        return "Verification failed", 403

    elif request.method == "POST":
        data = request.json
        messages = data.get("entry", [])[0].get("changes", [])[0].get("value", {}).get("messages", [])

        if messages:
            message_body = messages[0].get("text", {}).get("body", "")
            wa_id = messages[0].get("from", "")

            ai_response = generate_ai_response(message_body)
            send_whatsapp_message(wa_id, ai_response)

        return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Use cloud-assigned port
    app.run(host="0.0.0.0", port=port)
    #app.run(port=8000, debug=True)
