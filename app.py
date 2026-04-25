from flask import Flask, render_template, request, jsonify
import imaplib
import email
import time
import re
import threading
import traceback
import config
from tracker import start_tracking, get_flight_status, send_simple_email

app = Flask(__name__)

# --- WEB ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/track', methods=['POST'])
def web_track():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Invalid JSON request'}), 400
            
        flight_num = data.get('flight_number', '').strip().upper()
        user_email = data.get('email', '').strip().lower()
        
        if not flight_num or not user_email:
            return jsonify({'error': 'Flight number and email are required'}), 400
        
        print(f"🌐 Web Tracking Request: {flight_num} for {user_email}")
        
        # Normalize flight number
        flight_match = re.search(r'([A-Z0-9]{2})\s?(\d{3,4})', flight_num)
        if flight_match:
            normalized_flight = flight_match.group(1) + flight_match.group(2)
            result = start_tracking(None, normalized_flight, email=user_email)
            
            # Clean up the response for the web UI
            clean_msg = result.replace('*', '').replace('✈️', '').strip()
            
            if "✅" in result:
                # Send confirmation email immediately
                subject = f"✈️ Tracking Confirmed: {normalized_flight}"
                send_simple_email(user_email, subject, clean_msg)
                return jsonify({'message': clean_msg}), 200
            else:
                return jsonify({'error': clean_msg}), 400
        else:
            return jsonify({'error': 'Invalid flight number format (e.g. AA 123)'}), 400
            
    except Exception as e:
        print("❌ WEB TRACK ERROR:")
        traceback.print_exc()
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

# --- EMAIL BOT ENGINE ---

class AirBuddyEmailBot:
    def __init__(self):
        self.user = config.SMTP_USER
        self.password = config.SMTP_PASSWORD
        self.server = config.IMAP_SERVER
        self.port = config.IMAP_PORT

    def connect(self):
        try:
            self.mail = imaplib.IMAP4_SSL(self.server, self.port)
            self.mail.login(self.user, self.password)
            self.mail.select('inbox')
            return True
        except Exception as e:
            print(f"❌ IMAP Connection failed: {e}")
            return False

    def process_emails(self):
        try:
            _, data = self.mail.search(None, 'UNSEEN')
            if not data or not data[0]: return
            
            for num in data[0].split():
                _, msg_data = self.mail.fetch(num, '(RFC822)')
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                sender = email.utils.parseaddr(msg['From'])[1]
                subject = msg.get('Subject', '')
                
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            payload = part.get_payload(decode=True)
                            if isinstance(payload, bytes):
                                body = payload.decode(errors='ignore')
                            break
                else:
                    payload = msg.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        body = payload.decode(errors='ignore')
                
                self.handle_command(sender, body.strip(), subject=subject)
        except Exception as e:
            print(f"⚠️ Email processing error: {e}")

    def handle_command(self, sender, text, subject=""):
        if not text or len(text) > 2000: return
        
        msg = text.upper().strip()
        subj = subject.upper().strip()
        
        # Only process if:
        # A) Subject contains 'AIRBUDDY'
        # B) Body is JUST a flight number (max 10 chars)
        # C) Body is a direct command
        is_direct_ask = subj == "AIRBUDDY" or "AIRBUDDY" in subj
        is_pure_flight = re.fullmatch(r"([A-Z0-9]{2})\s?(\d{3,4})", msg)
        is_command = msg in ['LIST', 'HELP', 'STOP']
        
        if not (is_direct_ask or is_pure_flight or is_command):
            # Optional: Log but don't respond to save credits/noise
            return

        print(f"📩 Processing AirBuddy request from {sender}")
        
        # Commands
        if msg in ['HI', 'HELLO', 'START', 'MENU', 'HELP']:
            response = (
                "👋 Welcome to AirBuddy\n"
                "Your friendly flight tracking companion\n\n"
                "✈️ Quick Start:\n"
                "Reply with any flight number (e.g. AA 1234) to start tracking.\n\n"
                "📱 Commands:\n"
                "• LIST — Your active flights\n"
                "• STOP [flight] — Cancel tracking\n"
                "• HELP — This menu"
            )
            send_simple_email(sender, "Welcome to AirBuddy!", response)
            return

        if msg == 'LIST':
            response = get_tracked_flights_by_email(sender)
            send_simple_email(sender, "Your Active Flights", response)
            return

        # Track
        flight = re.search(r'([A-Z0-9]{2})\s?(\d{3,4})', msg)
        if flight:
            flight_num = flight.group(1) + flight.group(2)
            result = start_tracking(None, flight_num, email=sender)
            send_simple_email(sender, f"Tracking Confirmed: {flight_num}", result.replace('*', ''))
        else:
            send_simple_email(sender, "AirBuddy Assistant", "🤔 I didn't catch that flight number. Example: AA 123")

def get_tracked_flights_by_email(email_addr):
    import sqlite3
    conn = sqlite3.connect('flights.db')
    c = conn.cursor()
    flights = c.execute('SELECT flight_number FROM flights WHERE email = ? AND active = 1', (email_addr,)).fetchall()
    conn.close()
    if not flights: return "No active flights found."
    msg = "📋 Your Active Flights:\n\n"
    for f in flights: msg += f"• {f[0]}\n"
    return msg

def email_bot_thread():
    bot = AirBuddyEmailBot()
    if bot.connect():
        print("🚀 AirBuddy Email Engine is LIVE!")
        while True:
            bot.process_emails()
            time.sleep(30)
            try:
                bot.mail.noop()
            except:
                bot.connect()

if __name__ == '__main__':
    from db import init_db
    init_db()
    
    # Start Email Bot in background
    threading.Thread(target=email_bot_thread, daemon=True).start()
    
    print("🌐 AirBuddy Web Server starting...")
    app.run(port=5000, debug=False)
