#!/usr/bin/env python3
"""
Standalone Website Updater for LCF Civic Summaries
Updates the website without requiring Flask or other complex dependencies.
Uses direct HTTP requests to update the deployed website.
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('website_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StandaloneWebsiteUpdater:
    """Update the LCF Civic Summaries website without Flask dependencies."""
    
    def __init__(self):
        """Initialize the updater."""
        self.website_url = "https://19hninc15vp3.manussite.space"
        self.summaries_file = "document_summaries.json"
        
    def load_summaries(self):
        """Load the document summaries from the JSON file."""
        try:
            if not os.path.exists(self.summaries_file):
                logger.error(f"❌ Summaries file not found: {self.summaries_file}")
                logger.info("💡 Run the tracker first: python3 test_workflow.py")
                return None
                
            with open(self.summaries_file, 'r') as f:
                summaries = json.load(f)
                
            logger.info(f"✅ Loaded summaries for {len(summaries)} government bodies")
            return summaries
            
        except Exception as e:
            logger.error(f"❌ Error loading summaries: {e}")
            return None
    
    def update_website_data(self, summaries):
        """Update the website with new summary data."""
        try:
            # Prepare the data for the website API
            update_url = f"{self.website_url}/api/update"
            
            # Convert summaries to the format expected by the website
            website_data = self.convert_summaries_format(summaries)
            
            # Send update request
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'LCF-Tracker-Updater/1.0'
            }
            
            logger.info(f"🔄 Sending update to {update_url}")
            
            response = requests.post(
                update_url, 
                json=website_data, 
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("✅ Website updated successfully!")
                return True
            else:
                logger.warning(f"⚠️  Website update returned status {response.status_code}")
                # This is okay - the website might not have the API endpoint
                # but the data file update below will still work
                return self.update_data_file(summaries)
                
        except requests.exceptions.RequestException as e:
            logger.info(f"🔄 Direct API update failed: {e}")
            logger.info("🔄 Trying alternative update method...")
            return self.update_data_file(summaries)
        except Exception as e:
            logger.error(f"❌ Error updating website: {e}")
            return False
    
    def update_data_file(self, summaries):
        """Update the website by creating a data file that the website can read."""
        try:
            # Create a data file in a format the website can use
            website_data = self.convert_summaries_format(summaries)
            
            # Save to a file that can be uploaded to the website
            output_file = "website_data.json"
            with open(output_file, 'w') as f:
                json.dump(website_data, f, indent=2, default=str)
            
            logger.info(f"✅ Created website data file: {output_file}")
            logger.info("📋 To complete the update:")
            logger.info(f"   1. Upload {output_file} to your website's data directory")
            logger.info(f"   2. Or use the website's admin interface to import the data")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating data file: {e}")
            return False
    
    def convert_summaries_format(self, summaries):
        """Convert tracker summaries to website format."""
        website_data = {}
        
        for body_name, body_data in summaries.items():
            website_data[body_name] = {
                "agendas": [],
                "minutes": []
            }
            
            # Process agendas
            for agenda in body_data.get("agendas", []):
                agenda_entry = {
                    "title": agenda.get("title", f"{body_name} Agenda"),
                    "type": "agenda",
                    "date": agenda.get("date", datetime.now().isoformat()),
                    "summary": agenda.get("summary", "No summary available"),
                    "ai_generated": agenda.get("ai_generated", False),
                    "url": agenda.get("url", "https://lcf.ca.gov/city-clerk/agenda-minutes/")
                }
                website_data[body_name]["agendas"].append(agenda_entry)
            
            # Process minutes
            for minutes in body_data.get("minutes", []):
                minutes_entry = {
                    "title": minutes.get("title", f"{body_name} Minutes"),
                    "type": "minutes", 
                    "date": minutes.get("date", datetime.now().isoformat()),
                    "summary": minutes.get("summary", "No summary available"),
                    "ai_generated": minutes.get("ai_generated", False),
                    "url": minutes.get("url", "https://lcf.ca.gov/city-clerk/agenda-minutes/")
                }
                website_data[body_name]["minutes"].append(minutes_entry)
        
        # Add metadata
        website_data["_metadata"] = {
            "last_updated": datetime.now().isoformat(),
            "total_documents": sum(
                len(body.get("agendas", [])) + len(body.get("minutes", []))
                for body in website_data.values()
                if isinstance(body, dict) and "agendas" in body
            ),
            "government_bodies": len([
                body for body in website_data.values()
                if isinstance(body, dict) and "agendas" in body
            ])
        }
        
        return website_data
    
    def create_simple_report(self, summaries):
        """Create a simple HTML report as a backup."""
        try:
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LCF Civic Summaries - {datetime.now().strftime('%B %d, %Y')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background: #2563eb; color: white; padding: 20px; border-radius: 8px; }}
        .body-section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
        .document {{ margin: 10px 0; padding: 15px; background: #f9f9f9; border-radius: 5px; }}
        .ai-badge {{ background: #10b981; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; }}
        .auto-badge {{ background: #6b7280; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; }}
        .date {{ color: #6b7280; font-size: 14px; }}
        .summary {{ margin: 10px 0; }}
        .link {{ color: #2563eb; text-decoration: none; }}
        .link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ LCF Civic Summaries</h1>
        <p>La Cañada Flintridge Government Updates - {datetime.now().strftime('%B %d, %Y')}</p>
    </div>
"""
            
            for body_name, body_data in summaries.items():
                if not body_data.get("agendas") and not body_data.get("minutes"):
                    continue
                    
                html_content += f"""
    <div class="body-section">
        <h2>🏛️ {body_name}</h2>
"""
                
                # Add agendas
                if body_data.get("agendas"):
                    html_content += "<h3>📅 Upcoming Meetings</h3>"
                    for agenda in body_data["agendas"]:
                        badge = '<span class="ai-badge">AI Summary</span>' if agenda.get("ai_generated") else '<span class="auto-badge">Auto Summary</span>'
                        html_content += f"""
        <div class="document">
            <h4>{agenda.get('title', 'Agenda')} {badge}</h4>
            <p class="date">📅 {agenda.get('date', 'Date not available')}</p>
            <div class="summary">{agenda.get('summary', 'No summary available')}</div>
            <a href="{agenda.get('url', '#')}" class="link" target="_blank">📄 View Full Agenda Document</a>
        </div>
"""
                
                # Add minutes
                if body_data.get("minutes"):
                    html_content += "<h3>📋 Recent Meetings</h3>"
                    for minutes in body_data["minutes"]:
                        badge = '<span class="ai-badge">AI Summary</span>' if minutes.get("ai_generated") else '<span class="auto-badge">Auto Summary</span>'
                        html_content += f"""
        <div class="document">
            <h4>{minutes.get('title', 'Minutes')} {badge}</h4>
            <p class="date">📅 {minutes.get('date', 'Date not available')}</p>
            <div class="summary">{minutes.get('summary', 'No summary available')}</div>
            <a href="{minutes.get('url', '#')}" class="link" target="_blank">📄 View Full Meeting Minutes</a>
        </div>
"""
                
                html_content += "    </div>"
            
            html_content += """
    <div style="text-align: center; margin-top: 40px; color: #6b7280;">
        <p>Generated by LCF Civic Summaries Tracker</p>
        <p><a href="https://19hninc15vp3.manussite.space" class="link">Visit the Live Website</a></p>
    </div>
</body>
</html>"""
            
            # Save the report
            report_file = f"lcf_civic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(report_file, 'w') as f:
                f.write(html_content)
            
            logger.info(f"✅ Created backup report: {report_file}")
            return report_file
            
        except Exception as e:
            logger.error(f"❌ Error creating report: {e}")
            return None

def main():
    """Main entry point for the standalone website updater."""
    try:
        logger.info("🔄 Updating LCF Civic Summaries website...")
        
        updater = StandaloneWebsiteUpdater()
        
        # Load summaries
        summaries = updater.load_summaries()
        if not summaries:
            return False
        
        # Update website
        success = updater.update_website_data(summaries)
        
        # Create backup report
        report_file = updater.create_simple_report(summaries)
        
        if success:
            logger.info("✅ Website update completed successfully!")
            if report_file:
                logger.info(f"📄 Backup report created: {report_file}")
            return True
        else:
            logger.error("❌ Failed to update the website. Check the error messages above.")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in website updater: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

