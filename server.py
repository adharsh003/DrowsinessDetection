from flask import Flask, request, jsonify
from twilio.rest import Client
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS

# Twilio Credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
EMERGENCY_CONTACT = os.getenv("EMERGENCY_CONTACT")

if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, EMERGENCY_CONTACT]):
    raise ValueError("One or more environment variables are missing!")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# 📌 Route for sending drowsiness alert (Requires Location)
@app.route("/send_alert", methods=["POST"])
def send_alert():
    data = request.json
    print("📩 Received Data:", data)  # Debugging

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not latitude or not longitude:
        print("❌ Error: Invalid location data")
        return jsonify({"error": "Invalid location data"}), 400

    location_url = f"https://www.google.com/maps?q={latitude},{longitude}"
    message_body = f"🚨 Emergency! Driver is drowsy. Location: {location_url}"

    try:
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=EMERGENCY_CONTACT
        )
        print("✅ Drowsy SMS Sent! Response:", message.sid)  # Debugging
        return jsonify({"message": "Drowsiness alert sent!", "sid": message.sid}), 200
    except Exception as e:
        print("🚨 Twilio Error:", str(e))  # Debugging
        return jsonify({"error": str(e)}), 500


# 📌 Route for sending "Driver is awake" alert (No Location Required)
@app.route("/send_awake_alert", methods=["POST"])
def send_awake_alert():
    print("📢 Driver is Awake!")  # Debugging

    message_body = "✅ The driver is awake and alert."

    try:
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=EMERGENCY_CONTACT
        )
        print("✅ Awake SMS Sent! Response:", message.sid)  # Debugging
        return jsonify({"message": "Awake alert sent!", "sid": message.sid}), 200
    except Exception as e:
        print("🚨 Twilio Error:", str(e))  # Debugging
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
