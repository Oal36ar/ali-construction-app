#!/usr/bin/env python3
"""
LangChain Tools for Email Management
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailInput(BaseModel):
    """Input schema for email tools"""
    to_email: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    content: str = Field(..., description="Email content/body")
    from_name: str = Field(default="AI Assistant", description="Sender name")


class SendEmailTool(BaseTool):
    """Tool for sending emails"""
    name = "send_email"
    description = """Send an email to a specified recipient. 
    Use this when user wants to send, email, or notify someone.
    Examples: 'send email to...', 'email john about...', 'notify sarah that...'"""
    args_schema: Type[BaseModel] = EmailInput
    
    def _run(self, to_email: str, subject: str, content: str, from_name: str = "AI Assistant") -> str:
        """Execute the send email function"""
        try:
            # For demo purposes, we'll simulate sending an email
            # In production, you'd configure real SMTP settings
            
            # Validate email format
            if "@" not in to_email:
                return f"❌ Invalid email address: {to_email}"
            
            # Mock email sending (replace with real SMTP in production)
            email_log = {
                "to": to_email,
                "subject": subject,
                "content": content[:100] + "..." if len(content) > 100 else content,
                "from": from_name,
                "sent_at": datetime.now().isoformat(),
                "status": "sent"
            }
            
            # Log email attempt
            print(f"📧 Email sent to {to_email}: {subject}")
            
            return f"✅ Email sent successfully to {to_email}\n📧 Subject: {subject}\n✉️ From: {from_name}"
        except Exception as e:
            return f"❌ Failed to send email: {str(e)}"

    async def _arun(self, to_email: str, subject: str, content: str, from_name: str = "AI Assistant") -> str:
        """Async version of the tool"""
        return self._run(to_email, subject, content, from_name)


class ContactInput(BaseModel):
    """Input schema for contact parsing"""
    text: str = Field(..., description="Text content to parse for contact information")


class ParseContactsTool(BaseTool):
    """Tool for parsing contact information from text"""
    name = "parse_contacts"
    description = """Parse and extract contact information from text. 
    Use this when user wants to extract, find, or parse contact details.
    Examples: 'extract contacts from...', 'find emails in...', 'parse contact info from...'"""
    args_schema: Type[BaseModel] = ContactInput
    
    def _run(self, text: str) -> str:
        """Execute the parse contacts function"""
        try:
            import re
            
            # Extract email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            
            # Extract phone numbers (simple pattern)
            phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            phones = re.findall(phone_pattern, text)
            
            # Extract names (basic pattern - words that start with capital letters)
            name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
            names = re.findall(name_pattern, text)
            
            # Remove duplicates
            emails = list(set(emails))
            phones = list(set(phones))
            names = list(set(names))
            
            if not emails and not phones and not names:
                return "📝 No contact information found in the text."
            
            result = "📋 Extracted contact information:\n"
            
            if emails:
                result += f"📧 Emails ({len(emails)}):\n"
                for email in emails:
                    result += f"  • {email}\n"
            
            if phones:
                result += f"📞 Phone numbers ({len(phones)}):\n"
                for phone in phones:
                    result += f"  • {phone}\n"
            
            if names:
                result += f"👤 Names ({len(names)}):\n"
                for name in names:
                    result += f"  • {name}\n"
            
            return result
        except Exception as e:
            return f"❌ Failed to parse contacts: {str(e)}"

    async def _arun(self, text: str) -> str:
        """Async version of the tool"""
        return self._run(text) 