import requests
import sqlite3
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import config
import smtplib
import time
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Global API Cache to save credits
flight_cache = {}

# Daily Rate Limiting
MAX_CALLS = 80
calls_made = 0
last_reset_date = datetime.now().date()

def start_tracking(phone, flight_num, email=None):
    """Add flight to DB, return confirmation"""
    conn = sqlite3.connect('flights.db')
    c = conn.cursor()
    
    # Check if flight exists in API
    status = get_flight_status(flight_num)
    if not status:
        return (
            "✈️ Flight Not Found\n\n"
            f"We couldn't locate flight {flight_num} in our system.\n\n"
            "💡 Please check:\n"
            "• Flight number is correct (e.g. AA 1234)\n"
            "• Flight is scheduled for today or next 48h\n"
            "• Airline code matches (2 letters + 3-4 digits)"
        )
    
    try:
        # Check if already tracking for this email
        existing = c.execute('SELECT id FROM flights WHERE email = ? AND flight_number = ? AND active = 1', (email, flight_num)).fetchone()
        if existing:
            return f"✅ Already Tracking {flight_num}. You will receive alerts via email."

        c.execute('''
            INSERT INTO flights (phone, email, flight_number, last_delay, last_checked)
            VALUES (?, ?, ?, ?, ?)
        ''', (None, email, flight_num, status['delay'], datetime.now()))
        
        conn.commit()
    except Exception as e:
        return f"❌ Technical Issue: {str(e)[:50]}"
    finally:
        conn.close()
    
    delay_status = "On Time ✅" if status['delay'] == 0 else f"{status['delay']} minutes"
    
    return (
        f"✅ Now Tracking {flight_num}\n\n"
        f"📍 Route: {status['route']}\n"
        f"📊 Status: {status['status'].capitalize()}\n"
        f"⏳ Current Delay: {delay_status}\n"
        f"🚪 Gate: {status['gate']}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🔔 Smart Alerts Enabled\n"
        f"We'll notify you instantly via email if the delay increases!\n\n"
        f"Have a smooth journey! ✈️"
    )

def get_flight_status(flight_num):
    """Fetch from AviationStack API with caching & normalization"""
    flight_num_raw = flight_num.upper().strip()
    
    # 1. Smart Extraction (Only match at the start of words)
    match = re.search(r"\b([A-Z0-9]{2})\s?(\d{3,4})\b", flight_num_raw)
    if not match:
        print(f"❌ Invalid flight format: {flight_num}")
        return None

    flight_num = match.group(1) + match.group(2)
    print(f"🧪 Extracted flight: {flight_num}")

    # 2. Handle Mocks (Now matching the regex format)
    if flight_num == 'ST123':
        # Returns a delay that increases every minute (for testing alerts)
        mock_delay = (int(time.time() / 60) % 60) * 5 
        return {'status': 'active', 'delay': mock_delay, 'route': 'SFO → DXB', 'gate': 'A1'}
    
    if flight_num == 'TE123':
        return {'status': 'scheduled', 'delay': 0, 'route': 'JFK → LHR', 'gate': 'B12'}

    # 3. Check Cache (10 minute TTL)
    if flight_num in flight_cache:
        data, timestamp = flight_cache[flight_num]
        if time.time() - timestamp < 600:
            print(f"⚡ Using cached data for {flight_num}")
            return data
            
    # 5. Fetch from API (Safe Call with Daily Cap)
    global calls_made, last_reset_date
    
    # Reset counter if a new day has started
    if datetime.now().date() > last_reset_date:
        calls_made = 0
        last_reset_date = datetime.now().date()
        print("🌅 Daily API counter reset.")

    if calls_made >= MAX_CALLS:
        print("⚠️ Daily API limit reached! Skipping call.")
        return {'status': 'Limit Reached', 'delay': 0, 'route': 'N/A', 'gate': 'N/A', 'error': 'limit'}

    url = "http://api.aviationstack.com/v1/flights"
    params = {
        'access_key': config.AVIATION_KEY,
        'flight_iata': flight_num
    }
    
    try:
        calls_made += 1
        print(f"📡 API Call #{calls_made} for {flight_num}")
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        
        if 'data' not in data or not data['data']:
            print(f"⚠️ No flight data found for {flight_num}. Caching 'Not Found' status.")
            flight_cache[flight_num] = (None, time.time()) # Negative Cache
            return None
        
        flight = data['data'][0]
        dep = flight['departure']
        arr = flight['arrival']
        
        result = {
            'status': flight['flight_status'],
            'delay': dep.get('delay', 0) or 0,
            'route': f"{dep['iata']} → {arr['iata']}",
            'gate': dep.get('gate', 'TBA')
        }
        
        # Save to cache
        flight_cache[flight_num] = (result, time.time())
        return result
    except Exception as e:
        print(f"❌ Error fetching flight status: {e}")
        return None

def check_all_flights():
    """Background job - runs every 5 mins"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Checking active flights...")
    conn = sqlite3.connect('flights.db')
    c = conn.cursor()
    
    flights = c.execute('SELECT id, email, flight_number, last_delay FROM flights WHERE active = 1').fetchall()
    
    for flight in flights:
        fid, email, flight_num, last_delay = flight
        current = get_flight_status(flight_num)
        if not current or not current.get('status'): 
            continue
        
        current_delay = current.get('delay', 0)
        flight_status = current['status'].lower()
        
        # 1. Alert if delay increased
        if current_delay > last_delay + 15:
            send_email_alert(email, flight_num, current_delay, current['status'])
            c.execute('UPDATE flights SET last_delay = ?, last_checked = ? WHERE id = ?', (current_delay, datetime.now(), fid))
        
        # 2. Cleanup
        if flight_status in ['landed', 'cancelled', 'diverted']:
            c.execute('UPDATE flights SET active = 0 WHERE id = ?', (fid,))
            msg = (f"✅ Flight {flight_num} {flight_status.capitalize()}\n\n"
                   f"This flight is no longer being tracked.\n"
                   f"Hope you had a smooth journey! ✈️")
            send_simple_email(email, f"Flight Update: {flight_num}", msg)
        else:
            c.execute('UPDATE flights SET last_checked = ? WHERE id = ?', (datetime.now(), fid))
    
    conn.commit()
    conn.close()

def send_html_email(to_email, subject, title, message, flight_num=None):
    """Sends a professional branded HTML email"""
    if not to_email: return
    
    msg = MIMEMultipart("alternative")
    msg['From'] = f"AirBuddy <{config.SMTP_FROM}>"
    msg['To'] = to_email
    msg['Subject'] = subject

    # Branded Template
    html = f"""
    <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 10px; overflow: hidden;">
                <div style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">✈️ AirBuddy</h1>
                    <p style="color: #bfdbfe; margin: 5px 0 0 0;">Your flight tracking companion</p>
                </div>
                <div style="padding: 30px;">
                    <h2 style="color: #1e40af; margin-top: 0;">{title}</h2>
                    <div style="background: #f8fafc; border-radius: 8px; padding: 20px; margin: 20px 0; border-left: 4px solid #3b82f6;">
                        <pre style="white-space: pre-wrap; font-family: inherit; font-size: 16px; margin: 0;">{message}</pre>
                    </div>
                    <p style="font-size: 14px; color: #64748b;">
                        We are monitoring your flight 24/7. You will receive an instant alert if any delays are detected.
                    </p>
                </div>
                <div style="background: #f1f5f9; padding: 20px; text-align: center; font-size: 12px; color: #94a3b8;">
                    &copy; 2024 AirBuddy. All rights reserved.<br>
                    To stop tracking, reply to this email with <strong>STOP {flight_num if flight_num else ''}</strong>
                </div>
            </div>
        </body>
    </html>
    """
    
    msg.attach(MIMEText(message, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"📧 HTML Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send HTML email: {e}")

def send_simple_email(to_email, subject, body):
    """Old text-only fallback, now upgraded to HTML"""
    send_html_email(to_email, subject, "Update from AirBuddy", body)

def send_email_alert(to_email, flight_num, delay_mins, status):
    """Send detailed Email alert"""
    if not to_email: return
    subject = f"⚠️ AirBuddy Delay Alert: {flight_num}"
    title = f"Delay Detected: {flight_num}"
    body = (
        f"Significant Status Change Found!\n\n"
        f"• Status: {status.capitalize()}\n"
        f"• New Delay: {delay_mins} minutes\n\n"
        "Please check with your airline for latest gate and timing info."
    )
    send_html_email(to_email, subject, title, body, flight_num=flight_num)

# Start background scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(check_all_flights, 'interval', minutes=1)
scheduler.start()
print("⏰ Background scheduler started")