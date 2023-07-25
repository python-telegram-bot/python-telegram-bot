"""
Step 1. Get the flask app running locally.
    Run app below. Go to 127.0.0.1:5000
    Should see "Hello, World"
Step 2. Set up domain site
    Sign up for account on ngrok
    Navigate to flaskExample.py in terminal
    Run app on ngrok with  `ngrok http 5000`
    Confirm this works by going to the forwarding address given in terminal
        Ex: https://aaa-000-111-22-333.ngrok-free.app
    Should see "Hello, World"
    The terminal will log as "GET / HTTP/1.1" 200"
Step 3. Initialize Webhook
    ngrok will give a forwarding address
    You'll need to initialize the webhook with the following command
    https://api.telegram.org/bot${BOT_KEY}/setWebhook?url=${forwardingAddr}/hook 
    The easiest way is either with a post request via postman or by filling out the values manually then putting this in terminal:
    curl -X POST
    https://api.telegram.org/bot${BOT_KEY}/setWebhook?url=${forwardingAddr}/hook 
"""


BOT_KEY = "yourKey"
forwardingAddr = ""

from flask import Flask, request
import requests

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def hook():
    print(request.data)
    return "Hello, World."


@app.route("/hook", methods=["POST"])
def respond():
    update = request.get_json()
    chat_id = update["message"]["chat"]["id"]
    text = update["message"]["text"]
    if text.lower() == "what is your name":
        send_message("James", chat_id)
    else:
        send_message(text, chat_id)
    return "ok"


def send_message(text, chat_id):
    url = f"https://api.telegram.org/bot{BOT_KEY}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)


if __name__ == "__main__":
    app.run()
