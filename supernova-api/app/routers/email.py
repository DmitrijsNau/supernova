from fastapi import APIRouter, Request, Response, UploadFile
import smtplib
from pydantic import BaseModel

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


router: APIRouter = APIRouter()


class EmailRequest(BaseModel):
    to: list[str]
    subject: str
    body: str


def create_message(text, html):
    message_alternative = MIMEMultipart("alternative")
    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message_alternative.attach(part1)
    message_alternative.attach(part2)
    # add attachment
    message_mixed = MIMEMultipart("mixed")
    message_mixed.attach(message_alternative)
    return message_mixed


def send_email(
    server, subject, sender_email, receiver_email_list, message: MIMEMultipart
):
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_email_list)
    with smtplib.SMTP(server) as server:
        server.sendmail(sender_email, receiver_email_list, message.as_string())


@router.post("")
def get_document_type(email_request: EmailRequest):
    message = create_message(
        "this is a text test", "<div>this is a <strong>html</strong> test</div>"
    )
    send_email(
        "smtprelay.linde.grp",
        "LG&E Account Nexus Notification",
        "LG&E Account Nexus Notification <lge.account.nexus.notification@linde.com>",
        ["dmitrijs.naudzuns@linde.com", "gunther.kroth@linde.com"],
        message,
    )
    return {"message": "Email sent successfully."}
