from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---------------- SUMMARY + REPLY ----------------
def generate_summary_and_reply(body, sender_name, tone):
    try:
        prompt = f"""
        Email from: {sender_name}

        Email content:
        {body}

        First write a short summary.
        Then write a reply in {tone} tone.

        Format:

        Summary:
        ...

        Reply:
        ...
        """

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        return response.text

    except Exception as e:
        print("AI ERROR:", e)
        return "Error generating reply"


# ---------------- CLASSIFICATION ----------------
def classify_email(subject, body):
    try:
        prompt = f"""
        Classify this email into:
        Work, Personal, Promotion, Spam

        Subject: {subject}
        Body: {body}

        Only return category name.
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt
        )

        return response.text.strip()

    except:
        return "Work"


# ---------------- INBOX SUMMARY ----------------
def summarize_inbox(all_emails_text):
    try:
        prompt = f"""
        Summarize these emails:

        {all_emails_text}
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt
        )

        return response.text

    except:
        return "Error generating summary"


# ---------------- PRIORITY SCORE ----------------
def generate_priority_score(subject, body):
    try:
        prompt = f"""
        Give priority score from 0 to 100.

        Subject: {subject}
        Body: {body}

        Only return number.
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt
        )

        return int(response.text.strip())

    except:
        return 50


# ---------------- MEETING DETECTION (NEW) ----------------
def detect_meeting_details(email_body):
    try:
        prompt = f"""
        Extract meeting details from this email.

        Email:
        {email_body}

        Return in this format only:
        Title:
        Date:
        Time:
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt
        )

        return response.text

    except Exception as e:
        print("Meeting Detection Error:", e)
        return None