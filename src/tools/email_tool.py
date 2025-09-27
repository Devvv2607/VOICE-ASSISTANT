"""
Email management tool for checking and sending emails.
"""

import json
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun


class EmailTool(BaseTool):
    """LangChain tool for email operations."""
    
    name = "email_manager"
    description = "Check latest emails or send emails. Use 'check' to get latest emails or JSON with 'to', 'subject' to send."
    
    def __init__(self, email_config):
        super().__init__()
        self.email_user = email_config.get('user')
        self.email_password = email_config.get('password')
        self.email_imap_server = email_config.get('imap_server', 'imap.gmail.com')
        self.email_smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Handle email operations."""
        if not self.email_user or not self.email_password:
            return "Email is not configured."
        
        try:
            if query.lower() == 'check':
                return self._check_emails()
            else:
                # Try to parse as JSON for sending email
                params = json.loads(query) if query.startswith('{') else {}
                return self._send_email(params)
        except Exception as e:
            return f"Email operation failed: {str(e)}"
    
    def _check_emails(self):
        """Check latest emails."""
        try:
            mail = imaplib.IMAP4_SSL(self.email_imap_server)
            mail.login(self.email_user, self.email_password)
            mail.select('inbox')
            
            result, data = mail.search(None, 'ALL')
            email_ids = data[0].split()
            
            if not email_ids:
                return "No emails in inbox."
            
            latest_emails = []
            for email_id in email_ids[-3:]:
                result, msg_data = mail.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                
                subject = msg['subject'] or 'No Subject'
                sender = msg['from'] or 'Unknown Sender'
                date = msg['date'] or 'Unknown Date'
                
                latest_emails.append(f"From: {sender}\nSubject: {subject}")
            
            mail.close()
            mail.logout()
            
            return "Latest emails:\n" + "\n---\n".join(latest_emails)
            
        except Exception as e:
            return f"Error checking emails: {str(e)}"
    
    def _send_email(self, params):
        """Send an email."""
        try:
            to_email = params.get('to')
            subject = params.get('subject', 'Message from Jarvis')
            body = params.get('body', 'This is a message sent by Jarvis AI Assistant.')
            
            if not to_email:
                return "Need email address to send message."
            
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_smtp_server, 587)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            return f"Email sent successfully to {to_email}"
            
        except Exception as e:
            return f"Error sending email: {str(e)}"