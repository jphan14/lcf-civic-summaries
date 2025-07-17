#!/usr/bin/env python3
"""
La Canada Flintridge Government Meetings Tracker - Email Reporter
Compiles and sends consolidated email reports of meeting summaries.
"""

import os
import sys
import json
import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lcf_government_reporter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmailReporter:
    """Compiles and sends email reports of meeting summaries."""
    
    def __init__(self, config_path="config.json"):
        """Initialize the email reporter with configuration."""
        self.config = self.load_config(config_path)
    
    def load_config(self, config_path):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found. Using default settings.")
            return self.get_default_config()
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file {config_path}. Using default settings.")
            return self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration."""
        return {
            "send_email": False,
            "email_from": "lcf-tracker@example.com",
            "email_to": "user@example.com",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "",
            "smtp_password": "",
            "smtp_use_tls": True,
            "organize_by": "group"
        }
    
    def format_date(self, date_str):
        """Format date string for display."""
        if not date_str:
            return "Unknown Date"
        
        try:
            if isinstance(date_str, str):
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                date_obj = date_str
            return date_obj.strftime("%B %d, %Y")
        except:
            return str(date_str)
    
    def generate_html_report(self, summaries_data):
        """Generate HTML email report from summaries."""
        if not summaries_data:
            return self.generate_no_data_report()
        
        # Calculate date range for report
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #2c5aa0;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 14px;
        }}
        .content {{
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 0 0 8px 8px;
        }}
        .body-section {{
            background-color: white;
            margin: 20px 0;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .body-title {{
            color: #2c5aa0;
            font-size: 20px;
            font-weight: bold;
            margin: 0 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #2c5aa0;
        }}
        .document-item {{
            margin: 15px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-left: 4px solid #2c5aa0;
            border-radius: 0 4px 4px 0;
        }}
        .document-title {{
            font-weight: bold;
            color: #2c5aa0;
            margin-bottom: 5px;
        }}
        .document-date {{
            font-size: 12px;
            color: #666;
            margin-bottom: 10px;
        }}
        .document-summary {{
            line-height: 1.5;
        }}
        .no-documents {{
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 20px;
        }}
        .footer {{
            margin-top: 30px;
            padding: 20px;
            background-color: #e9ecef;
            border-radius: 8px;
            font-size: 12px;
            color: #666;
            text-align: center;
        }}
        .summary-stats {{
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .summary-stats h3 {{
            margin: 0 0 10px 0;
            color: #1976d2;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>La Cañada Flintridge Government Update</h1>
        <p>Weekly Summary of City Council and Commission Activities</p>
        <p>{start_date.strftime("%B %d")} - {end_date.strftime("%B %d, %Y")}</p>
    </div>
    
    <div class="content">
"""
        
        # Generate summary statistics
        total_documents = 0
        bodies_with_activity = 0
        
        for body_name, body_data in summaries_data.items():
            body_total = len(body_data.get("agendas", [])) + len(body_data.get("minutes", []))
            total_documents += body_total
            if body_total > 0:
                bodies_with_activity += 1
        
        html += f"""
        <div class="summary-stats">
            <h3>This Week's Activity</h3>
            <p><strong>{total_documents}</strong> documents from <strong>{bodies_with_activity}</strong> government bodies</p>
        </div>
"""
        
        # Generate content for each government body
        for body_name, body_data in summaries_data.items():
            agendas = body_data.get("agendas", [])
            minutes = body_data.get("minutes", [])
            
            if not agendas and not minutes:
                continue
            
            html += f"""
        <div class="body-section">
            <div class="body-title">{body_name}</div>
"""
            
            # Add agendas
            if agendas:
                for agenda in agendas:
                    html += f"""
            <div class="document-item">
                <div class="document-title">📋 {agenda.get('title', 'Agenda')}</div>
                <div class="document-date">{self.format_date(agenda.get('date'))}</div>
                <div class="document-summary">{agenda.get('summary', 'No summary available.')}</div>
            </div>
"""
            
            # Add minutes
            if minutes:
                for minute in minutes:
                    html += f"""
            <div class="document-item">
                <div class="document-title">📝 {minute.get('title', 'Minutes')}</div>
                <div class="document-date">{self.format_date(minute.get('date'))}</div>
                <div class="document-summary">{minute.get('summary', 'No summary available.')}</div>
            </div>
"""
            
            html += """
        </div>
"""
        
        # Add footer
        html += f"""
        <div class="footer">
            <p>This report was automatically generated by the La Cañada Flintridge Government Tracker.</p>
            <p>For complete meeting documents, visit <a href="https://lcf.ca.gov/city-clerk/agenda-minutes/">lcf.ca.gov</a></p>
            <p>Report generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def generate_no_data_report(self):
        """Generate a report when no data is available."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #2c5aa0;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }}
        .content {{
            background-color: #f9f9f9;
            padding: 40px;
            text-align: center;
            border-radius: 0 0 8px 8px;
        }}
        .footer {{
            margin-top: 20px;
            padding: 20px;
            background-color: #e9ecef;
            border-radius: 8px;
            font-size: 12px;
            color: #666;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>La Cañada Flintridge Government Update</h1>
        <p>Weekly Summary Report</p>
    </div>
    
    <div class="content">
        <h2>No New Activity This Week</h2>
        <p>There were no new meeting documents available for the reporting period.</p>
        <p>This could be due to:</p>
        <ul style="text-align: left; display: inline-block;">
            <li>No scheduled meetings this week</li>
            <li>Documents not yet published online</li>
            <li>Technical issues accessing the city website</li>
        </ul>
        <p>The system will continue monitoring for new documents.</p>
    </div>
    
    <div class="footer">
        <p>This report was automatically generated by the La Cañada Flintridge Government Tracker.</p>
        <p>For complete meeting documents, visit <a href="https://lcf.ca.gov/city-clerk/agenda-minutes/">lcf.ca.gov</a></p>
        <p>Report generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
    </div>
</body>
</html>
"""
        return html
    
    def generate_text_report(self, summaries_data):
        """Generate plain text email report from summaries."""
        if not summaries_data:
            return self.generate_no_data_text_report()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        text = f"""
LA CAÑADA FLINTRIDGE GOVERNMENT UPDATE
Weekly Summary of City Council and Commission Activities
{start_date.strftime("%B %d")} - {end_date.strftime("%B %d, %Y")}

{'='*60}

"""
        
        # Generate summary statistics
        total_documents = 0
        bodies_with_activity = 0
        
        for body_name, body_data in summaries_data.items():
            body_total = len(body_data.get("agendas", [])) + len(body_data.get("minutes", []))
            total_documents += body_total
            if body_total > 0:
                bodies_with_activity += 1
        
        text += f"THIS WEEK'S ACTIVITY: {total_documents} documents from {bodies_with_activity} government bodies\n\n"
        
        # Generate content for each government body
        for body_name, body_data in summaries_data.items():
            agendas = body_data.get("agendas", [])
            minutes = body_data.get("minutes", [])
            
            if not agendas and not minutes:
                continue
            
            text += f"{body_name.upper()}\n"
            text += "-" * len(body_name) + "\n\n"
            
            # Add agendas
            for agenda in agendas:
                text += f"AGENDA: {agenda.get('title', 'Unknown')}\n"
                text += f"Date: {self.format_date(agenda.get('date'))}\n"
                text += f"Summary: {agenda.get('summary', 'No summary available.')}\n\n"
            
            # Add minutes
            for minute in minutes:
                text += f"MINUTES: {minute.get('title', 'Unknown')}\n"
                text += f"Date: {self.format_date(minute.get('date'))}\n"
                text += f"Summary: {minute.get('summary', 'No summary available.')}\n\n"
            
            text += "\n"
        
        text += f"""
{'='*60}

This report was automatically generated by the La Cañada Flintridge Government Tracker.
For complete meeting documents, visit: https://lcf.ca.gov/city-clerk/agenda-minutes/
Report generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
"""
        
        return text
    
    def generate_no_data_text_report(self):
        """Generate a plain text report when no data is available."""
        text = f"""
LA CAÑADA FLINTRIDGE GOVERNMENT UPDATE
Weekly Summary Report
{datetime.now().strftime("%B %d, %Y")}

{'='*60}

NO NEW ACTIVITY THIS WEEK

There were no new meeting documents available for the reporting period.

This could be due to:
- No scheduled meetings this week
- Documents not yet published online
- Technical issues accessing the city website

The system will continue monitoring for new documents.

{'='*60}

This report was automatically generated by the La Cañada Flintridge Government Tracker.
For complete meeting documents, visit: https://lcf.ca.gov/city-clerk/agenda-minutes/
Report generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
"""
        return text
    
    def send_email_report(self, summaries_data):
        """Send the email report."""
        if not self.config.get("send_email", False):
            logger.info("Email sending is disabled in configuration")
            return False
        
        try:
            # Generate email content
            html_content = self.generate_html_report(summaries_data)
            text_content = self.generate_text_report(summaries_data)
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"La Cañada Flintridge Government Update - {datetime.now().strftime('%B %d, %Y')}"
            msg['From'] = self.config.get("email_from", "lcf-tracker@example.com")
            msg['To'] = self.config.get("email_to", "user@example.com")
            
            # Attach text and HTML versions
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            smtp_server = self.config.get("smtp_server", "smtp.gmail.com")
            smtp_port = self.config.get("smtp_port", 587)
            smtp_username = self.config.get("smtp_username", "")
            smtp_password = self.config.get("smtp_password", "")
            use_tls = self.config.get("smtp_use_tls", True)
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            
            if use_tls:
                server.starttls()
            
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email report sent successfully to {msg['To']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email report: {e}")
            return False
    
    def save_report_to_file(self, summaries_data):
        """Save the report to HTML and text files."""
        try:
            # Generate reports
            html_content = self.generate_html_report(summaries_data)
            text_content = self.generate_text_report(summaries_data)
            
            # Save HTML report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"lcf_government_report_{timestamp}.html"
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Save text report
            text_filename = f"lcf_government_report_{timestamp}.txt"
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            logger.info(f"Reports saved to {html_filename} and {text_filename}")
            return html_filename, text_filename
            
        except Exception as e:
            logger.error(f"Failed to save reports to files: {e}")
            return None, None
    
    def generate_and_send_report(self, summaries_data=None):
        """Main method to generate and send the consolidated report."""
        logger.info("Starting email report generation...")
        
        # Load summaries data if not provided
        if summaries_data is None:
            try:
                with open("document_summaries.json", 'r') as f:
                    summaries_data = json.load(f)
            except FileNotFoundError:
                logger.error("No document summaries found. Run summarize_all_meetings.py first.")
                return False
            except json.JSONDecodeError:
                logger.error("Invalid JSON in document_summaries.json")
                return False
        
        # Save reports to files
        html_file, text_file = self.save_report_to_file(summaries_data)
        
        # Send email if configured
        email_sent = self.send_email_report(summaries_data)
        
        # U        # Update the website with new data
        try:
            import subprocess
            result = subprocess.run([
                'python3', 'update_website_standalone.py'
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                logger.info("✅ Website updated successfully")
            else:
                logger.warning(f"⚠️ Website update had issues: {result.stderr}")
        except Exception as e:
            logger.warning(f"⚠️ Could not update website: {e}")
        
        # Append to historical archive
        try:
            import subprocess
            result = subprocess.run([
                'python3', 'append_to_archive.py'
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                logger.info("✅ Historical archive updated successfully")
            else:
                logger.warning(f"⚠️ Archive update had issues: {result.stderr}")
        except Exception as e:
            logger.warning(f"⚠️ Could not update historical archive: {e}")
        
        if email_sent:
            logger.info("Email report process completed successfully")
        else:
            logger.info("Email report generated and saved to files (email sending disabled or failed)")
        
        return True

def main():
    """Main entry point for the script."""
    try:
        reporter = EmailReporter()
        success = reporter.generate_and_send_report()
        
        if success:
            logger.info("Email reporting completed successfully")
            return True
        else:
            logger.error("Email reporting failed")
            return False
            
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return False

if __name__ == "__main__":
    main()

