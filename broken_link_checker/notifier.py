"""Notifier module."""

# Import smtplib for the actual sending function
import smtplib
# Here are the email package modules we'll need
from email.message import EmailMessage


class Notifier:
    """
    Notify by email.

    :smtp_server represent the address of the email service provider
    :username represent the email of the sender
    :password represent the password of the sender
    """

    def __init__(self, smtp_server: str, username: str, password: str):
        """Init the notifier."""
        self.smtp_server = smtp_server
        self.sender = username
        self.password = password

    def send(self, recipient: str, subject: str, body: str) -> None:
        """
        Send an email.

        :recipient represent the email of the dest
        :subject represent the subject of the notification
        :body represent the content of the notification
        """
        # Create the container email message.
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = recipient
        msg.set_content(body)

        # Send the message via our own SMTP server.
        s = smtplib.SMTP(self.smtp_server)
        s.starttls()
        s.login(self.sender, self.password)
        s.send_message(msg)
        s.quit()
