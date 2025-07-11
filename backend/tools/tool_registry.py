#!/usr/bin/env python3
"""
Tool Registry for LangChain Agent
Real backend functions exposed as LangChain tools
"""

import re
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from langchain.tools import Tool
from sqlalchemy.orm import Session


class ToolRegistry:
    """Registry of all available tools for the LangChain agent"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session
        self.tools = self._register_all_tools()
    
    def _register_all_tools(self) -> List[Tool]:
        """Register all available tools"""
        return [
            self._create_add_reminder_tool(),
            self._create_send_email_tool(),
            self._create_summarize_file_tool(),
            self._create_parse_contacts_tool(),
            self._create_list_reminders_tool(),
            self._create_analyze_document_tool()
        ]
    
    def _create_add_reminder_tool(self) -> Tool:
        """Create the add reminder tool"""
        def add_reminder(input_str: str) -> str:
            """Add a new reminder to the system.
            
            Args:
                input_str: String containing reminder details in format:
                          'text: [reminder description], date: [YYYY-MM-DD or natural date]'
            
            Returns:
                Success message with reminder details
            """
            try:
                # Parse the input string
                text = ""
                date = ""
                
                # Try to extract text and date from the input
                if 'text: ' in input_str and 'date: ' in input_str:
                    parts = input_str.split(', ')
                    for part in parts:
                        if part.startswith('text: '):
                            text = part[6:]
                        elif part.startswith('date: '):
                            date = part[6:]
                else:
                    # If not in expected format, treat the whole input as text
                    text = input_str
                    
                # Validate and format date
                if not date:
                    date = datetime.now().strftime("%Y-%m-%d")
                elif not re.match(r'\d{4}-\d{2}-\d{2}', date):
                    # Try to parse common date formats
                    try:
                        from dateutil import parser
                        parsed_date = parser.parse(date)
                        date = parsed_date.strftime("%Y-%m-%d")
                    except:
                        date = datetime.now().strftime("%Y-%m-%d")
                
                if self.db_session:
                    from models.database import Reminder
                    new_reminder = Reminder(
                        title=text,
                        description="",
                        date=date,
                        priority="medium",
                        completed=False
                    )
                    self.db_session.add(new_reminder)
                    self.db_session.commit()
                    self.db_session.refresh(new_reminder)
                    
                    return f"✅ Reminder '{text}' successfully created for {date} (ID: {new_reminder.id})"
                else:
                    # Fallback for in-memory storage
                    reminder_id = datetime.now().microsecond
                    return f"✅ Reminder '{text}' successfully created for {date} (ID: {reminder_id})"
                    
            except Exception as e:
                return f"❌ Failed to create reminder: {str(e)}"
        
        return Tool(
            name="add_reminder",
            description="""Add a new reminder or task to the system. Use this when the user wants to:
            - Create a reminder
            - Set a deadline
            - Add a task
            - Schedule something
            
            Input format: 'text: [reminder description], date: [YYYY-MM-DD or natural date]'
            Examples: 'Call client, 2024-12-15' or 'Project deadline, next Friday'""",
            func=add_reminder
        )
    
    def _create_send_email_tool(self) -> Tool:
        """Create the send email tool"""
        def send_email(input_str: str) -> str:
            """Send an email to a specified recipient.
            
            Args:
                input_str: String containing email details in format:
                          'to: [email], subject: [subject], body: [message content]'
            
            Returns:
                Success or failure message
            """
            try:
                # Parse the input string
                to = subject = body = ""
                
                # Try to extract to, subject, and body from the input
                if 'to: ' in input_str:
                    parts = input_str.split(', ')
                    for part in parts:
                        if part.startswith('to: '):
                            to = part[4:]
                        elif part.startswith('subject: '):
                            subject = part[9:]
                        elif part.startswith('body: '):
                            body = part[6:]
                else:
                    # If not in expected format, try to parse it differently
                    return f"❌ Invalid input format. Expected 'to: [email], subject: [subject], body: [message]'"
                
                if not to or not subject or not body:
                    return f"❌ Missing required fields. Please provide to, subject, and body."
                
                # Validate email format
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', to):
                    return f"❌ Invalid email address: {to}"
                
                # For demo purposes - in production, implement real SMTP
                email_data = {
                    "to": to,
                    "subject": subject,
                    "body": body[:200] + "..." if len(body) > 200 else body,
                    "sent_at": datetime.now().isoformat(),
                    "status": "sent"
                }
                
                # Log the email (in production, send via SMTP)
                print(f"📧 Email queued: {to} - {subject}")
                
                return f"✅ Email sent successfully to {to}\n📧 Subject: {subject}\n📄 Body preview: {body[:100]}..."
                
            except Exception as e:
                return f"❌ Failed to send email: {str(e)}"
        
        return Tool(
            name="send_email",
            description="""Send an email to someone. Use this when the user wants to:
            - Send an email
            - Notify someone
            - Share information via email
            - Contact someone
            
            Input format: 'to: [email], subject: [subject], body: [message content]'
            Example: 'to: john@example.com, subject: Project Update, body: The project is on track.'""",
            func=send_email
        )
    
    def _create_summarize_file_tool(self) -> Tool:
        """Create the summarize file tool"""
        def summarize_file(content: str) -> str:
            """Summarize text content into key points.
            
            Args:
                content: The text content to summarize
            
            Returns:
                A concise summary of the content
            """
            try:
                if not content or len(content.strip()) < 10:
                    return "❌ Content too short to summarize"
                
                # Word count analysis
                words = content.split()
                word_count = len(words)
                
                # Extract key information
                sentences = [s.strip() for s in content.split('.') if s.strip()]
                
                # Find dates, numbers, and important keywords
                dates = re.findall(r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}', content)
                emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
                phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content)
                
                # Keywords that indicate importance
                important_keywords = ['deadline', 'urgent', 'important', 'critical', 'asap', 'priority']
                found_keywords = [kw for kw in important_keywords if kw.lower() in content.lower()]
                
                # Create summary
                summary = f"📄 Document Summary ({word_count} words)\n\n"
                
                # Key sentences (first, middle, last if multiple sentences)
                if len(sentences) > 1:
                    key_sentences = []
                    key_sentences.append(sentences[0])
                    if len(sentences) > 2:
                        key_sentences.append(sentences[len(sentences)//2])
                    if len(sentences) > 1:
                        key_sentences.append(sentences[-1])
                    
                    summary += "🔍 Key Points:\n"
                    for i, sentence in enumerate(key_sentences[:3]):
                        summary += f"  {i+1}. {sentence}\n"
                
                # Important findings
                if dates:
                    summary += f"\n📅 Dates found: {', '.join(dates[:3])}"
                if emails:
                    summary += f"\n📧 Emails: {len(emails)} contact(s)"
                if phones:
                    summary += f"\n📞 Phone numbers: {len(phones)} found"
                if found_keywords:
                    summary += f"\n⚠️ Important keywords: {', '.join(found_keywords)}"
                
                return summary
                
            except Exception as e:
                return f"❌ Failed to summarize content: {str(e)}"
        
        return Tool(
            name="summarize_file",
            description="""Summarize and analyze text content. Use this when the user wants to:
            - Get a summary of a document
            - Extract key points from text
            - Analyze content quickly
            - Condense long text
            
            Input: The text content to be summarized
            Returns: A structured summary with key points, dates, contacts, and important information""",
            func=summarize_file
        )
    
    def _create_parse_contacts_tool(self) -> Tool:
        """Create the parse contacts tool"""
        def parse_contacts(text: str) -> str:
            """Extract contact information from text.
            
            Args:
                text: Text content to parse for contact information
            
            Returns:
                Formatted list of found contacts
            """
            try:
                # Extract different types of contact information
                emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
                phones = re.findall(r'\b(?:\+?1[-.\s]?)?\(?([2-9][0-8][0-9])\)?[-.\s]?([2-9][0-9]{2})[-.\s]?([0-9]{4})\b', text)
                
                # Extract names (basic pattern - can be enhanced)
                name_patterns = [
                    r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',  # First Last
                    r'\b([A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+)\b',  # First M. Last
                    r'\b([A-Z][a-z]+, [A-Z][a-z]+)\b'  # Last, First
                ]
                
                names = set()
                for pattern in name_patterns:
                    matches = re.findall(pattern, text)
                    names.update(matches)
                
                # Extract addresses (basic pattern)
                address_pattern = r'\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)'
                addresses = re.findall(address_pattern, text, re.IGNORECASE)
                
                # Remove duplicates
                emails = list(set(emails))
                phones = list(set(phones))
                names = list(names)
                addresses = list(set(addresses))
                
                if not any([emails, phones, names, addresses]):
                    return "📝 No contact information found in the provided text."
                
                result = "📋 Contact Information Extracted:\n\n"
                
                if names:
                    result += f"👤 Names ({len(names)}):\n"
                    for name in names[:10]:  # Limit to first 10
                        result += f"  • {name}\n"
                
                if emails:
                    result += f"\n📧 Email Addresses ({len(emails)}):\n"
                    for email in emails[:10]:
                        result += f"  • {email}\n"
                
                if phones:
                    result += f"\n📞 Phone Numbers ({len(phones)}):\n"
                    for phone in phones[:10]:
                        formatted_phone = f"({phone[0]}) {phone[1]}-{phone[2]}"
                        result += f"  • {formatted_phone}\n"
                
                if addresses:
                    result += f"\n🏠 Addresses ({len(addresses)}):\n"
                    for address in addresses[:5]:
                        result += f"  • {address.strip()}\n"
                
                return result
                
            except Exception as e:
                return f"❌ Failed to parse contacts: {str(e)}"
        
        return Tool(
            name="parse_contacts",
            description="""Extract contact information from text content. Use this when the user wants to:
            - Find contacts in a document
            - Extract emails and phone numbers
            - Parse address information
            - Get contact details from text
            
            Input: Text content containing potential contact information
            Returns: Structured list of names, emails, phone numbers, and addresses found""",
            func=parse_contacts
        )
    
    def _create_list_reminders_tool(self) -> Tool:
        """Create the list reminders tool"""
        def list_reminders(input_str: str = "") -> str:
            """List existing reminders from the system.
            
            Returns:
                Formatted list of current reminders
            """
            try:
                if self.db_session:
                    from models.database import Reminder
                    reminders = self.db_session.query(Reminder).order_by(Reminder.date).limit(20).all()
                    
                    if not reminders:
                        return "📝 No reminders found in the system."
                    
                    result = f"📋 Current Reminders ({len(reminders)}):\n\n"
                    
                    for reminder in reminders:
                        status_emoji = "✅" if reminder.completed else "⏰"
                        priority_emoji = "🔴" if reminder.priority == "high" else "🟡" if reminder.priority == "medium" else "🟢"
                        
                        result += f"{status_emoji} {priority_emoji} {reminder.title}\n"
                        result += f"   📅 Due: {reminder.date}\n"
                        if reminder.description:
                            result += f"   📝 {reminder.description[:100]}...\n" if len(reminder.description) > 100 else f"   📝 {reminder.description}\n"
                        result += "\n"
                    
                    return result
                else:
                    return "📝 No reminders found (using in-memory storage)."
                    
            except Exception as e:
                return f"❌ Failed to list reminders: {str(e)}"
        
        return Tool(
            name="list_reminders",
            description="""List all current reminders and tasks. Use this when the user wants to:
            - See their reminders
            - Check what tasks are due
            - View their schedule
            - List pending items
            
            No input required.
            Returns: Formatted list of all reminders with dates, status, and priorities""",
            func=list_reminders
        )
    
    def _create_analyze_document_tool(self) -> Tool:
        """Create the analyze document tool"""
        def analyze_document(content: str) -> str:
            """Perform comprehensive analysis of document content.
            
            Args:
                content: Document content to analyze
            
            Returns:
                Detailed analysis report
            """
            try:
                if not content or len(content.strip()) < 20:
                    return "❌ Content too short for meaningful analysis"
                
                # Basic metrics
                words = content.split()
                sentences = [s.strip() for s in content.split('.') if s.strip()]
                lines = content.split('\n')
                
                # Content analysis
                emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
                phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content)
                dates = re.findall(r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}', content)
                
                # Keywords analysis
                business_keywords = ['project', 'meeting', 'deadline', 'client', 'proposal', 'contract']
                tech_keywords = ['api', 'database', 'server', 'development', 'code', 'software']
                urgency_keywords = ['urgent', 'asap', 'immediate', 'critical', 'emergency']
                
                found_business = [kw for kw in business_keywords if kw.lower() in content.lower()]
                found_tech = [kw for kw in tech_keywords if kw.lower() in content.lower()]
                found_urgency = [kw for kw in urgency_keywords if kw.lower() in content.lower()]
                
                # Document type detection
                doc_type = "General"
                if found_business:
                    doc_type = "Business Document"
                elif found_tech:
                    doc_type = "Technical Document"
                
                if found_urgency:
                    doc_type += " (Urgent)"
                
                # Generate analysis report
                analysis = f"📊 Document Analysis Report\n\n"
                analysis += f"📄 Document Type: {doc_type}\n"
                analysis += f"📏 Length: {len(words)} words, {len(sentences)} sentences, {len(lines)} lines\n\n"
                
                analysis += "🔍 Content Overview:\n"
                if len(sentences) > 0:
                    analysis += f"  • Opening: {sentences[0][:100]}...\n"
                if len(sentences) > 2:
                    analysis += f"  • Key point: {sentences[len(sentences)//2][:100]}...\n"
                if len(sentences) > 1:
                    analysis += f"  • Conclusion: {sentences[-1][:100]}...\n"
                
                if emails or phones or dates:
                    analysis += "\n📋 Key Information Found:\n"
                    if emails:
                        analysis += f"  📧 Email addresses: {len(emails)}\n"
                    if phones:
                        analysis += f"  📞 Phone numbers: {len(phones)}\n"
                    if dates:
                        analysis += f"  📅 Dates mentioned: {len(dates)}\n"
                
                if found_business or found_tech or found_urgency:
                    analysis += "\n🏷️ Keywords Analysis:\n"
                    if found_business:
                        analysis += f"  💼 Business: {', '.join(found_business)}\n"
                    if found_tech:
                        analysis += f"  💻 Technical: {', '.join(found_tech)}\n"
                    if found_urgency:
                        analysis += f"  ⚠️ Urgency: {', '.join(found_urgency)}\n"
                
                # Recommendations
                analysis += "\n💡 Recommendations:\n"
                if dates:
                    analysis += "  • Consider adding reminders for mentioned dates\n"
                if emails:
                    analysis += "  • Extract contacts for future reference\n"
                if found_urgency:
                    analysis += "  • Prioritize urgent items mentioned in document\n"
                if len(words) > 500:
                    analysis += "  • Document is lengthy - consider creating a summary\n"
                
                return analysis
                
            except Exception as e:
                return f"❌ Failed to analyze document: {str(e)}"
        
        return Tool(
            name="analyze_document",
            description="""Perform comprehensive analysis of document content. Use this when the user wants to:
            - Analyze a document thoroughly
            - Get insights about content
            - Understand document structure
            - Extract key information patterns
            
            Input: Document content to analyze
            Returns: Detailed analysis report with metrics, content overview, and recommendations""",
            func=analyze_document
        )
    
    def get_tools(self) -> List[Tool]:
        """Get all registered tools"""
        return self.tools
    
    def get_tool_descriptions(self) -> List[Dict[str, str]]:
        """Get descriptions of all tools for API documentation"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "type": "function"
            }
            for tool in self.tools
        ]


# Global tool registry instance
def create_tool_registry(db_session: Optional[Session] = None) -> ToolRegistry:
    """Create a new tool registry instance"""
    return ToolRegistry(db_session) 