from flask import Flask, redirect, session, request, render_template, send_file
from services.calendar_service import get_upcoming_events, create_event
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
import base64
import re
import csv
from reportlab.pdfgen import canvas

from services.llm_service import (
    generate_summary_and_reply,
    classify_email,
    summarize_inbox,
    generate_priority_score,
    detect_meeting_details
)

from services.gmail_service import send_email

app = Flask(__name__)
app.secret_key = "supersecretkey"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# ---------------- GLOBAL STORAGE ----------------
important_emails = []
reply_history = []
starred_emails = []
threads = {}
labels = {}
latest_emails = []

email_stats = {
    "total": 0,
    "Work": 0,
    "Personal": 0,
    "Promotion": 0,
    "Spam": 0,
    "replies_sent": 0
}

# ---------------- GOOGLE AUTH ----------------
flow = Flow.from_client_secrets_file(
    "credentials.json",
    scopes=[
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/calendar"
    ],
    redirect_uri="http://localhost:5000/callback"
)

# ---------------- EMAIL BODY ----------------
def get_email_body(payload):
    if "parts" in payload:
        for part in payload["parts"]:
            mime_type = part.get("mimeType")

            if mime_type == "text/plain":
                data = part["body"].get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

            elif mime_type == "text/html":
                data = part["body"].get("data")
                if data:
                    html = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                    return re.sub("<.*?>", "", html)

            elif "parts" in part:
                result = get_email_body(part)
                if result:
                    return result
    else:
        data = payload["body"].get("data")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    return ""

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    auth_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(auth_url)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes
    }

    return redirect("/emails")

# ---------------- CALENDAR (UPDATED ✅) ----------------
@app.route("/calendar")
def calendar():
    if "credentials" not in session:
        return redirect("/")

    credentials = Credentials(**session["credentials"])
    calendar_service = build("calendar", "v3", credentials=credentials)

    events = get_upcoming_events(calendar_service)

    return render_template("calendar.html", events=events)


@app.route("/create_event", methods=["POST"])
def create_event_route():
    if "credentials" not in session:
        return redirect("/")

    summary = request.form.get("summary")
    description = request.form.get("description")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")

    # ✅ FIX datetime format
    if start_time:
        start_time = start_time + ":00"
    if end_time:
        end_time = end_time + ":00"

    credentials = Credentials(**session["credentials"])
    calendar_service = build("calendar", "v3", credentials=credentials)

    create_event(calendar_service, summary, description, start_time, end_time)

    return redirect("/calendar")


# ✅ CREATE EVENT FROM EMAIL
@app.route("/create_event_from_email", methods=["POST"])
def create_event_from_email():
    if "credentials" not in session:
        return redirect("/")

    meeting_info = request.form.get("meeting_info")

    credentials = Credentials(**session["credentials"])
    calendar_service = build("calendar", "v3", credentials=credentials)

    try:
        lines = meeting_info.split("\n")

        title = lines[0].replace("Title:", "").strip()
        date = lines[1].replace("Date:", "").strip()
        time = lines[2].replace("Time:", "").strip()

        start_time = f"{date}T{time}:00"
        end_time = f"{date}T{time}:59"

        create_event(
            calendar_service,
            title,
            "Created from email",
            start_time,
            end_time
        )

    except Exception as e:
        print("Calendar Error:", e)

    return redirect("/calendar")

# ---------------- EMAILS ----------------
@app.route("/emails")
def emails():
    global latest_emails

    if "credentials" not in session:
        return redirect("/")

    credentials = Credentials(**session["credentials"])
    gmail_service = build("gmail", "v1", credentials=credentials)

    results = gmail_service.users().messages().list(
        userId="me", maxResults=5
    ).execute()

    messages = results.get("messages", [])
    emails_data = []

    email_stats.update({
        "total": 0,
        "Work": 0,
        "Personal": 0,
        "Promotion": 0,
        "Spam": 0
    })

    for message in messages:
        msg = gmail_service.users().messages().get(
            userId="me", id=message["id"], format="full"
        ).execute()

        headers = msg["payload"]["headers"]

        subject = "No Subject"
        sender_email = ""
        sender_name = ""

        for header in headers:
            if header["name"] == "Subject":
                subject = header["value"]

            if header["name"] == "From":
                sender_raw = header["value"]

                email_match = re.search(r"<(.+?)>", sender_raw)
                sender_email = email_match.group(1) if email_match else sender_raw

                name_match = re.match(r"(.*)<", sender_raw)
                sender_name = name_match.group(1).strip() if name_match else sender_email

        body = get_email_body(msg["payload"]).strip()

        try:
            category = classify_email(subject, body[:500])
        except:
            category = "Work"

        try:
            priority = generate_priority_score(subject, body[:500])
        except:
            priority = 50

        if category in email_stats:
            email_stats[category] += 1

        email_obj = {
            "id": message["id"],
            "sender": sender_name,
            "sender_email": sender_email,
            "subject": subject,
            "body": body[:300],
            "full_body": body,
            "category": category,
            "priority": priority,
        }

        emails_data.append(email_obj)

    latest_emails = emails_data
    email_stats["total"] = len(emails_data)

    return render_template("emails.html", emails=emails_data)

# ---------------- GENERATE REPLY ----------------
@app.route("/generate_reply", methods=["POST"])
def generate_reply():
    body = request.form.get("body")
    sender = request.form.get("sender")
    tone = request.form.get("tone")

    ai_reply = generate_summary_and_reply(body, sender, tone)
    meeting_info = detect_meeting_details(body)

    return render_template(
        "reply.html",
        ai_reply=ai_reply,
        sender=sender,
        tone=tone,
        meeting_info=meeting_info
    )

# ---------------- SEND REPLY ----------------
@app.route("/send_reply", methods=["POST"])
def send_reply():
    if "credentials" not in session:
        return redirect("/")

    to_email = request.form.get("to_email")
    subject = request.form.get("subject")
    reply = request.form.get("reply")

    credentials = Credentials(**session["credentials"])
    gmail_service = build("gmail", "v1", credentials=credentials)

    send_email(gmail_service, to_email, subject, reply)

    reply_history.append({
        "to": to_email,
        "subject": subject,
        "reply": reply
    })

    email_stats["replies_sent"] += 1

    return render_template("sent.html")

# ---------------- HISTORY ----------------
@app.route("/history")
def history():
    return render_template("history.html", history=reply_history)

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", stats=email_stats)

# ---------------- INBOX SUMMARY ----------------
@app.route("/inbox_summary")
def inbox_summary():
    if "credentials" not in session:
        return redirect("/")

    credentials = Credentials(**session["credentials"])
    gmail_service = build("gmail", "v1", credentials=credentials)

    results = gmail_service.users().messages().list(
        userId="me", maxResults=5
    ).execute()

    messages = results.get("messages", [])
    combined_text = ""

    for message in messages:
        msg = gmail_service.users().messages().get(
            userId="me", id=message["id"], format="full"
        ).execute()

        combined_text += get_email_body(msg["payload"]) + "\n\n"

    try:
        summary = summarize_inbox(combined_text[:3000])
    except:
        summary = "Inbox summary not available."

    return render_template("inbox_summary.html", summary=summary)

# ---------------- EXPORT CSV ----------------
@app.route("/export_csv")
def export_csv():
    file_path = "emails.csv"

    with open(file_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Sender", "Subject", "Category", "Priority"])

        for email in latest_emails:
            writer.writerow([
                email["sender"],
                email["subject"],
                email["category"],
                email["priority"]
            ])

    return send_file(file_path, as_attachment=True)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)