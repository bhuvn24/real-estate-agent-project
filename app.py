from flask import Flask, request
from flask_socketio import SocketIO, emit
import google.generativeai as genai  # <-- Changed from OpenAI
import os
import json
import pandas as pd
from dotenv import load_dotenv
from twilio.rest import Client
import random

load_dotenv()
app = Flask(__name__)
# Use eventlet for better performance with Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# --- Gemini API Configuration ---
# Make sure GEMINI_API_KEY is set in your .env file
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")  # Using a fast and capable model

# Dummy properties data (load from properties.json)
properties_df = pd.read_json("properties.json")


class GreetingAgent:
    def greet(self, user_input):
        try:
            # --- Use Gemini for natural response ---
            prompt = f"You are a friendly real estate consultant avatar. Respond naturally and conversationally to the user's message: '{user_input}'. Keep your response concise (1-2 sentences) and guide them towards asking about property details if relevant."

            # Generate content using the Gemini model
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error with Gemini API: {e}")
            # Fallback if no API key or error
            return "Hello! Tell me about the property you're interested in."


class RecommendationAgent:
    def recommend(self, prefs):  # prefs example: {'type': 'villa', 'price_max': 50000}
        filtered = properties_df[
            (properties_df["type"].str.lower() == prefs.get("type", "").lower())
            & (properties_df["price"] <= prefs.get("price_max", float("inf")))
        ]
        return filtered.to_dict(orient="records")[:3]


class EmotionAgent:
    def analyze(self, user_input):
        # Simplified text-based sentiment (keyword check)
        positive_keywords = ["great", "love", "interested", "yes", "perfect", "want"]
        negative_keywords = ["no", "bad", "expensive", "don't like"]
        score = 0.5  # Neutral
        if any(word in user_input.lower() for word in positive_keywords):
            score += 0.3
        if any(word in user_input.lower() for word in negative_keywords):
            score -= 0.3
        emotion = (
            "positive" if score > 0.5 else "negative" if score < 0.5 else "neutral"
        )
        return {"emotion": emotion, "interest": min(max(score, 0), 1)}


class NegotiationAgent:
    def negotiate(self, base_price, interest_score, seasonality=1.0):
        if interest_score > 0.7:
            # High interest means a smaller discount might be offered
            return round(base_price * 0.95 * seasonality)  # 5% discount
        if interest_score < 0.4:
            # Lower interest might prompt a better offer
            return round(base_price * 0.90 * seasonality)  # 10% discount
        return round(base_price * seasonality)


class FinanceAgent:
    def calculate_emi(self, principal, rate, tenure_months):
        monthly_rate = rate / 12 / 100
        emi = (
            principal
            * monthly_rate
            * (1 + monthly_rate) ** tenure_months
            / ((1 + monthly_rate) ** tenure_months - 1)
        )
        return round(emi, 2)

    def get_options(self, price):
        # Calculate loan amount assuming 80% LTV (Loan-to-Value)
        loan_amount = price * 0.80
        return {
            "5-Year Loan (8% APR)": f"${self.calculate_emi(loan_amount, 8, 60)}/month",
            "10-Year Loan (7% APR)": f"${self.calculate_emi(loan_amount, 7, 120)}/month",
        }


class FollowUpAgent:
    def __init__(self):
        try:
            self.client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))
            self.twilio_phone = os.getenv("TWILIO_PHONE")
        except Exception as e:
            self.client = None
            print(
                f"Twilio client failed to initialize: {e}. Follow-up messages will be disabled."
            )

    def send_message(self, to_phone, message):
        if not self.client or not self.twilio_phone:
            print("Skipping SMS follow-up because Twilio is not configured.")
            return
        try:
            self.client.messages.create(
                from_=self.twilio_phone, body=message, to=f"whatsapp:{to_phone}"
            )
            print(f"Follow-up sent to {to_phone}")
        except Exception as e:
            print(f"Failed to send Twilio message: {e}")


# Orchestrator
class Orchestrator:
    def __init__(self):
        self.greeting = GreetingAgent()
        self.recommend = RecommendationAgent()
        self.emotion = EmotionAgent()
        self.negotiate = NegotiationAgent()
        self.finance = FinanceAgent()
        self.followup = FollowUpAgent()

    def parse_prefs(self, user_input):
        prefs = {}
        lower_input = user_input.lower()
        if "villa" in lower_input:
            prefs["type"] = "villa"
        elif "apartment" in lower_input:
            prefs["type"] = "apartment"

        # Improved price parsing
        if (
            "under" in lower_input
            or "less than" in lower_input
            or "below" in lower_input
        ):
            try:
                # Find numbers in the input string
                numbers = [int(s) for s in lower_input.split() if s.isdigit()]
                if numbers:
                    prefs["price_max"] = max(numbers)  # Take the largest number found
            except:
                pass
        return prefs

    def process(self, user_input, to_phone=None, session_end=False):
        response = self.greeting.greet(user_input)
        prefs = self.parse_prefs(user_input)

        # Only recommend if preferences are detected
        recs = []
        if prefs:
            recs = self.recommend.recommend(prefs)

        engagement = self.emotion.analyze(user_input)

        if recs:
            # Add some dynamic elements to the response
            seasonality = random.uniform(0.95, 1.05)  # Dummy seasonality
            negotiated_price = self.negotiate.negotiate(
                recs[0]["price"], engagement["interest"], seasonality
            )
            recs[0]["negotiated_price"] = negotiated_price

            response += f"\n\nI found a great option for you! It's a {recs[0]['type']} in {recs[0]['location']}. Based on current demand, I can offer it for **${negotiated_price}**."

            if "loan" in user_input.lower() or "emi" in user_input.lower():
                options = self.finance.get_options(negotiated_price)
                loan_options_str = " and ".join(
                    [f"{k}: {v}" for k, v in options.items()]
                )
                response += f"\n\nFor financing, here are some estimated options based on an 80% loan: {loan_options_str}."

        if session_end and to_phone and recs:
            message = f"Thanks for your interest in the {recs[0]['type']} in {recs[0]['location']}! The special offered price is ${recs[0]['negotiated_price']}. Please reply to this message to connect with a human agent."
            self.followup.send_message(to_phone, message)
            response = "Thank you! I've sent the details to your WhatsApp. A representative will be in touch shortly."

        return response, recs


orchestrator = Orchestrator()


@socketio.on("user_message")
def handle_message(data):
    user_input = data["message"]
    to_phone = data.get("phone")
    session_end = data.get("session_end", False)
    response, recs = orchestrator.process(user_input, to_phone, session_end=session_end)
    emit("agent_response", {"text": response, "recommendations": recs})


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)
