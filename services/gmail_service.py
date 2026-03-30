import base64
from email.mime.text import MIMEText


def send_email(service, to, subject, message_text):

    if not to:
        print("No recipient email found")
        return

    message = MIMEText(message_text)

    message["to"] = to

    if subject.startswith("Re:"):
        message["subject"] = subject
    else:
        message["subject"] = "Re: " + subject

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    body = {
        "raw": raw_message
    }

    service.users().messages().send(
        userId="me",
        body=body
    ).execute()

    print("Email sent to:", to)