Here is a **professional README.md** for your project. You can copy this into `README.md` in your GitHub repo.


# 📧 AI Email Assistant (Email + Calendar + Generative AI)

## 🚀 Project Overview

**AI Email Assistant** is a smart productivity application that integrates **Gmail API, Google Calendar API, and Generative AI** to help users manage emails, generate replies, summarize inbox content, and schedule calendar events automatically.

This project demonstrates how modern AI applications combine **APIs, automation, and LLMs** to build real-world productivity tools.

---

# 🧠 Features

### 📧 Email Features

* Gmail Login using OAuth
* Read and display emails
* AI-generated email summaries
* AI-generated replies (different tones)
* Edit reply before sending
* Send replies via Gmail API
* Email classification (Work, Personal, Promotion, Spam)
* Email priority scoring
* Inbox summary generation
* Reply history
* Star important emails
* Export emails to CSV
* Export emails to PDF
* Dashboard with email statistics

### 📅 Calendar Features

* View upcoming Google Calendar events
* Create calendar events manually
* Detect meeting details from emails using AI
* Create calendar event directly from email

---

# 🛠 Technologies Used

* **Python**
* **Flask**
* **Gmail API**
* **Google Calendar API**
* **Generative AI (LLM API)**
* **HTML / CSS**
* **OAuth Authentication**
* **CSV & PDF Export**
* **Regex & Text Processing**

---

# 📂 Project Structure

```
ai-email-assistant/
│
├── app.py
├── credentials.json
├── token.json
├── .env
│
├── services/
│   ├── gmail_service.py
│   ├── llm_service.py
│   ├── calendar_service.py
│
├── templates/
│   ├── home.html
│   ├── emails.html
│   ├── reply.html
│   ├── sent.html
│   ├── history.html
│   ├── dashboard.html
│   ├── inbox_summary.html
│   ├── starred.html
│   ├── edit_reply.html
│   ├── calendar.html
│
├── static/
│   └── style.css
│
└── README.md
```

---

# 🔐 Setup Instructions

## 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/ai-email-assistant.git
cd ai-email-assistant
```

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

## 3️⃣ Install Requirements

```bash
pip install flask google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv reportlab
```

## 4️⃣ Add Google API Credentials

* Go to Google Cloud Console
* Enable Gmail API
* Enable Google Calendar API
* Download `credentials.json`
* Place it in project root folder

## 5️⃣ Add Environment Variables (.env)

```
GEMINI_API_KEY=your_api_key_here
```

## 6️⃣ Run Application

```bash
python app.py
```

Open:

```
http://localhost:5000
```

---

# 🤖 AI Capabilities

The system uses Generative AI to:

* Summarize emails
* Generate replies
* Classify emails
* Generate priority scores
* Summarize inbox
* Detect meeting details from emails

---

# 📊 Dashboard Statistics

The dashboard shows:

* Total emails
* Work emails
* Personal emails
* Spam emails
* Promotions
* Replies sent

---

# 🎯 Future Improvements

* Email search
* Email thread view
* Sentiment analysis
* Auto follow-up reminders
* Attachment handling
* Deploy on cloud (Render / Railway)
* Modern UI (Bootstrap / Tailwind)
* Database integration

---

# 👨‍💻 Author

**Your Name**

AI / Python Developer
Interested in Artificial Intelligence, Automation, and Productivity Tools

---

# ⭐ Conclusion

This project demonstrates how to build a **real-world AI-powered productivity assistant** that integrates email management, calendar scheduling, and AI-generated content into one system.



