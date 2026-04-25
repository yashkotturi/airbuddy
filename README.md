# ✈️ AirBuddy

### Your Friendly Flight Tracking Companion

AirBuddy is a lightweight, API-efficient flight tracking system that monitors flights in real-time and sends **smart email alerts** when delays or status changes occur.

Built with a focus on **minimal API usage**, **reliability**, and **clean system design**, AirBuddy ensures you never miss important flight updates — without burning through API credits.

---

## 🚀 Features

* ✈️ **Flight Tracking**
  Track any flight using flight number (e.g. `6E2045`, `AI101`)

* 📊 **Live Status Monitoring**
  Get real-time updates on:
  * Flight status (active, delayed, landed)
  * Delay duration
  * Route (departure → arrival)
  * Gate information

* 🔔 **Smart Alerts**
  * Alerts only when delay increases
  * Avoids spam notifications
  * Automatic stop after landing/cancellation

* ⚡ **API Credit Optimization (Core Feature)**
  * Intelligent caching (10-min TTL)
  * Negative caching for failed queries
  * Daily API call limits
  * Deduplicated requests across users

* 📧 **Branded Email Notifications**
  * Clean HTML emails
  * Professional UI
  * Personalized alerts

* ⏰ **Background Scheduler**
  * Automatically checks flights every 1 minute (adjustable)
  * No manual refresh needed

---

## 🧠 System Design

AirBuddy is designed to be **efficient and scalable**, not just functional.

### 🔁 Flow
```
User Input → Validate → Cache Check → API Call → Store → Notify
```

### 🧩 Key Components

* **Flight Parser**
  * Extracts valid flight numbers from messy input
* **Caching Layer**
  * Reduces redundant API calls
* **Scheduler**
  * Periodic flight monitoring
* **Database (SQLite)**
  * Stores tracked flights & state
* **Email Engine**
  * Sends alerts via SMTP

---

## 🛠️ Tech Stack

* **Backend:** Python (Flask)
* **Database:** SQLite
* **Scheduler:** APScheduler
* **Email:** SMTP (Gmail)
* **API:** Aviationstack

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the repo
```bash
git clone https://github.com/yashkotturi/airbuddy.git
cd airbuddy
```

---

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

---

### 3️⃣ Configure environment
Create a `.env` file:
```env
AVIATIONSTACK_KEY=your_api_key

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

---

### 4️⃣ Run the app
```bash
python app.py
```

---

## 📌 Usage

1. Open the web interface (`localhost:5000`)
2. Enter:
   * Flight number (e.g. `6E 2045`)
   * Email address
3. Click **Track**
4. Receive alerts when delays change ✉️

---

## 🧪 Testing

Use mock flights:
* `TE 123` → Always on time (Success Test)
* `ST 123` → Increasing delay (Alert Stress Test)

---

## ⚡ Optimization Strategies (Why this project stands out)

AirBuddy is not just another API project — it is **engineered for efficiency**:
* 🔥 Caching reduces API usage by up to 80%
* 🔁 Deduplicates repeated flight requests
* 🚫 Blocks invalid inputs before API calls
* 📉 Enforces daily API limits

---

## 🤝 Contributing
Contributions are welcome!
```bash
# Fork → Create branch → Commit → PR
```

---

## 📄 License
MIT License

---

## 👩‍💻 Author
**Yashita Kotturi**
* GitHub: [https://github.com/yashkotturi](https://github.com/yashkotturi)

---

## ⭐ If you like this project
Give it a star ⭐ — it helps a lot!
