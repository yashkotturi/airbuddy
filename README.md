# ✈️ Flyo - Intelligent Flight Delay Tracker

> Your 24/7 WhatsApp companion for real-time flight delay alerts

Flyo monitors your flights and instantly notifies you via WhatsApp when delays increase, so you can adjust your plans without constantly checking airport boards.

---

## 🌟 Features

- **Smart Monitoring**: Checks flight status every 5 minutes using live aviation data
- **Instant Alerts**: WhatsApp notifications when delays increase by 15+ minutes
- **Multi-Flight Tracking**: Monitor multiple flights simultaneously
- **Simple Commands**: Natural language interface—just send a flight number
- **Always On**: 24/7 background monitoring with zero effort after setup

---

## 📱 User Experience

### Starting a conversation

```
User: Hi
Flyo: 👋 Welcome to Flyo
      Your intelligent flight companion

      We monitor your flights 24/7 and send instant WhatsApp 
      alerts when delays increase.

      ✈️ Quick Start:
      • Send any flight number (e.g. AA 1234 or 6E2045)
      • We'll confirm tracking and send updates automatically

      📱 Commands:
      • LIST — View all tracked flights
      • STOP [flight] — Cancel tracking
      • HELP — Show this menu

      Ready when you are. What flight would you like to track?
```

### Tracking a flight

```
User: 6E 2045

Flyo: ✅ Now Tracking 6E2045

      📍 Route: DEL → BLR
      📊 Status: Scheduled
      ⏳ Current Delay: On Time ✅
      🚪 Gate: 15

      ━━━━━━━━━━━━━━━━
      🔔 Smart Alerts Enabled
      We'll notify you instantly if:
      • Delay increases by 15+ minutes
      • Status changes significantly

      Have a smooth journey! ✈️
```

### Receiving an alert

```
Flyo: ⚠️ SIGNIFICANT DELAY

      Flight: 6E2045
      Status: Delayed
      Delay: 75 minutes

      ━━━━━━━━━━━━━━━━
      The delay has increased significantly since we last checked.

      💡 Tips:
      • Check with your airline for the latest gate info
      • Allow extra time for connections
      • We'll continue monitoring and update you

      Safe travels! ✈️

      —
      Flyo | Your flight companion
```

---

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8+
- Twilio account (with WhatsApp sandbox or approved business number)
- AviationStack API key (free tier available)

### 1. Clone and Install

```bash
git clone <your-repo>
cd flyo
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file:

```env
# Twilio Credentials
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# AviationStack API
AVIATIONSTACK_KEY=your_aviationstack_key
```

### 3. Initialize Database

The database will be created automatically on first run, or manually:

```bash
python db.py
```

### 4. Run the Application

```bash
python app.py
```

### 5. Expose Webhook (for Development)

Use ngrok to expose your local server:

```bash
ngrok http 5000
```

---

## 📊 Architecture

```
User (WhatsApp) 
    ↓
Twilio → Flask Webhook → tracker.py
                            ↓
                    ┌───────┴───────┐
                    ↓               ↓
            SQLite DB    AviationStack API
                    ↑               
    Background Scheduler (5min interval)
    Checks all flights → Sends alerts
```

---

## 🚀 Deployment

### Option 1: Heroku
### Option 2: Railway
### Option 3: AWS EC2 / DigitalOcean

---

## 🧪 Testing

1. Join Twilio WhatsApp sandbox
2. Send: `HI` to test welcome message
3. Send: `6E2045` to test tracking
4. Send: `LIST` to verify storage
5. Send: `STOP 6E2045` to test removal

---

## 📈 Enhancements (Roadmap)

- [ ] Gate change notifications
- [ ] Flight cancellation alerts
- [ ] Multi-language support
- [ ] Timezone-aware scheduling

---

## 📄 License

MIT License - feel free to modify and use for your projects!

**Built with ❤️ for travelers who value their time**
