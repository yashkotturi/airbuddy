# ✈️ AirBuddy - Professional Flight Tracking Companion

> Your 24/7 intelligent flight monitoring service with Web and Email integration.

AirBuddy monitors your flights and instantly notifies you via professional HTML emails when delays increase or status changes occur. No more refreshing airport boards—we do the work for you.

---

## 🌟 Features

- **Multi-Channel Tracking**: Sign up via our sleek **Web Dashboard** or just **Email** us a flight number.
- **Smart Monitoring**: Polls flight status using live aviation data with intelligent 10-minute caching.
- **Branded HTML Alerts**: Beautifully formatted email notifications for confirmations and delay alerts.
- **Credit-Saving Engine**: Built-in flight number normalization, validation, and a daily safety cap to optimize API usage.
- **Privacy First**: Local SQLite database storage and secure environment configuration.

---

## 🛠️ Technology Stack

- **Backend**: Python (Flask)
- **Database**: SQLite
- **Real-time Data**: AviationStack API
- **Automation**: APScheduler (Background monitoring)
- **Communication**: SMTP (Outbound alerts) & IMAP (Inbound commands)

---

## 🚀 Setup Instructions

### 1. Configure Environment
Create a `.env` file with your credentials:
```env
AVIATIONSTACK_KEY=your_key_here

# SMTP/IMAP (Gmail recommended)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
```

### 2. Run the Application
```bash
pip install -r requirements.txt
python app.py
```

### 3. Usage
- **Web**: Open `http://localhost:5000` to track flights via the UI.
- **Email**: Send an email to your bot's address with the Subject "AirBuddy" and a flight number (e.g., `AA 100`) in the body.

---

## 🧪 Demo Modes
- **Track `TE 123`**: Test a successful tracking confirmation.
- **Track `ST 123`**: Test a dynamic delay alert (increments delay every minute).

---

## 📄 License
MIT License - Built with ❤️ for travelers by AirBuddy.
