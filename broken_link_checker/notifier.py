# Import smtplib for the actual sending function
import smtplib
# Here are the email package modules we'll need
from email.message import EmailMessage


class Notifier:
    def __init__(self, smtp_server, username, password):
        self.smtp_server = smtp_server
        self.sender = username
        self.password = password

    def send(self, recipient, subject, body):
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
