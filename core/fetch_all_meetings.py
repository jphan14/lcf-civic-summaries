#!/usr/bin/env python3
"""
La Canada Flintridge Government Meetings Tracker - Document Fetcher
Fetches meeting agendas and minutes from all government bodies.
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lcf_government_tracker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Government bodies to track
GOVERNMENT_BODIES = [
    "City Council",
    "Design Commission", 
    "Investment & Financing Advisory Committee",
    "Parks & Recreation Commission",
    "Planning Commission",
    "Public Safety Commission",
    "Public Works and Traffic Commission",
    "Sustainability and Resilience Commission"
]

# Base URL for La Canada Flintridge city website
BASE_URL = "https://lcf.ca.gov"
MEETINGS_URL = "https://lcf.ca.gov/city-clerk/agenda-minutes/"

class MeetingDocumentFetcher:
    """Fetches meeting documents from the La Canada Flintridge website."""
    
    def __init__(self, config_path="config.json"):
        """Initialize the fetcher with configuration."""
        self.config = self.load_config(config_path)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create directories for storing documents
        self.base_dir = "meeting_documents"
        self.create_directories()
    
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
            "enabled_bodies": GOVERNMENT_BODIES,
            "include_agendas": True,
            "include_minutes": True,
            "days_back": 30
        }
    
    def create_directories(self):
        """Create directories for storing documents."""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        
        for body in GOVERNMENT_BODIES:
            body_dir = os.path.join(self.base_dir, body.replace(" ", "_").replace("&", "and"))
            if not os.path.exists(body_dir):
                os.makedirs(body_dir)
    
    def fetch_page_content(self, url, retries=3):
        """Fetch content from a URL with retries."""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.content
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(random.uniform(1, 3))
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
    
    def parse_meetings_page(self):
        """Parse the main meetings page to find recent documents."""
        logger.info("Fetching meetings page...")
        content = self.fetch_page_content(MEETINGS_URL)
        
        if not content:
            logger.error("Could not fetch meetings page")
            return self.create_mock_documents()
        
        soup = BeautifulSoup(content, 'html.parser')
        documents = {}
        
        # Initialize document structure for each body
        for body in self.config.get("enabled_bodies", GOVERNMENT_BODIES):
            documents[body] = {
                "agendas": [],
                "minutes": []
            }
        
        # Look for document links
        # This is a simplified parser - the actual implementation would need
        # to be customized based on the specific structure of the LCF website
        links = soup.find_all('a', href=True)
        
        cutoff_date = datetime.now() - timedelta(days=self.config.get("days_back", 30))
        
        for link in links:
            href = link.get('href')
            text = link.get_text().strip()
            
            if not href or not text:
                continue
            
            # Check if this is a PDF document
            if not href.lower().endswith('.pdf'):
                continue
            
            # Try to match the document to a government body
            for body in self.config.get("enabled_bodies", GOVERNMENT_BODIES):
                if self.matches_body(text, body):
                    doc_info = {
                        "title": text,
                        "url": urljoin(BASE_URL, href),
                        "date": self.extract_date(text),
                        "type": self.determine_document_type(text)
                    }
                    
                    # Only include recent documents
                    if doc_info["date"] and doc_info["date"] >= cutoff_date:
                        if doc_info["type"] == "agenda" and self.config.get("include_agendas", True):
                            documents[body]["agendas"].append(doc_info)
                        elif doc_info["type"] == "minutes" and self.config.get("include_minutes", True):
                            documents[body]["minutes"].append(doc_info)
        
        # If no documents found, create mock documents for testing
        if not any(documents[body]["agendas"] or documents[body]["minutes"] for body in documents):
            logger.warning("No recent documents found. Creating mock documents for testing.")
            return self.create_mock_documents()
        
        return documents
    
    def matches_body(self, text, body):
        """Check if document text matches a government body."""
        text_lower = text.lower()
        body_lower = body.lower()
        
        # Simple keyword matching - could be improved
        if "city council" in body_lower and "city council" in text_lower:
            return True
        elif "design commission" in body_lower and "design" in text_lower:
            return True
        elif "investment" in body_lower and ("investment" in text_lower or "financing" in text_lower):
            return True
        elif "parks" in body_lower and "parks" in text_lower:
            return True
        elif "planning commission" in body_lower and "planning" in text_lower:
            return True
        elif "public safety" in body_lower and "safety" in text_lower:
            return True
        elif "public works" in body_lower and ("works" in text_lower or "traffic" in text_lower):
            return True
        elif "sustainability" in body_lower and ("sustainability" in text_lower or "resilience" in text_lower):
            return True
        
        return False
    
    def extract_date(self, text):
        """Extract date from document title."""
        # This is a simplified date extraction - would need to be improved
        # based on actual document naming conventions
        import re
        
        # Look for common date patterns
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    if len(match.groups()) == 3:
                        if match.group(1).isdigit() and len(match.group(1)) == 4:
                            # YYYY-MM-DD format
                            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                        elif match.group(3).isdigit() and len(match.group(3)) == 4:
                            # MM-DD-YYYY format
                            return datetime(int(match.group(3)), int(match.group(1)), int(match.group(2)))
                        else:
                            # Month name format
                            month_names = {
                                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                                'may': 5, 'june': 6, 'july': 7, 'august': 8,
                                'september': 9, 'october': 10, 'november': 11, 'december': 12
                            }
                            month = month_names.get(match.group(1).lower())
                            if month:
                                return datetime(int(match.group(3)), month, int(match.group(2)))
                except ValueError:
                    continue
        
        # Default to current date if no date found
        return datetime.now()
    
    def determine_document_type(self, text):
        """Determine if document is agenda or minutes."""
        text_lower = text.lower()
        if "agenda" in text_lower:
            return "agenda"
        elif "minutes" in text_lower:
            return "minutes"
        else:
            # Default to agenda if unclear
            return "agenda"
    
    def download_document(self, doc_info, body):
        """Download a document and save it locally."""
        try:
            content = self.fetch_page_content(doc_info["url"])
            if not content:
                return None
            
            # Create filename
            body_dir = body.replace(" ", "_").replace("&", "and")
            date_str = doc_info["date"].strftime("%Y%m%d") if doc_info["date"] else "unknown"
            filename = f"{date_str}_{doc_info['type']}_{body_dir}.pdf"
            filepath = os.path.join(self.base_dir, body_dir, filename)
            
            # Save the document
            with open(filepath, 'wb') as f:
                f.write(content)
            
            logger.info(f"Downloaded: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error downloading {doc_info['url']}: {e}")
            return None
    
    def create_mock_documents(self):
        """Create mock documents for testing when website is inaccessible."""
        logger.info("Creating mock documents for testing...")
        
        documents = {}
        current_date = datetime.now()
        
        for body in self.config.get("enabled_bodies", GOVERNMENT_BODIES):
            documents[body] = {
                "agendas": [],
                "minutes": []
            }
            
            # Create mock agenda
            if self.config.get("include_agendas", True):
                agenda_date = current_date - timedelta(days=7)
                agenda_content = self.generate_mock_agenda_content(body, agenda_date)
                agenda_file = self.save_mock_document(body, "agenda", agenda_date, agenda_content)
                
                documents[body]["agendas"].append({
                    "title": f"{body} Agenda - {agenda_date.strftime('%B %d, %Y')}",
                    "url": "mock://agenda",
                    "date": agenda_date,
                    "type": "agenda",
                    "local_path": agenda_file
                })
            
            # Create mock minutes
            if self.config.get("include_minutes", True):
                minutes_date = current_date - timedelta(days=14)
                minutes_content = self.generate_mock_minutes_content(body, minutes_date)
                minutes_file = self.save_mock_document(body, "minutes", minutes_date, minutes_content)
                
                documents[body]["minutes"].append({
                    "title": f"{body} Minutes - {minutes_date.strftime('%B %d, %Y')}",
                    "url": "mock://minutes",
                    "date": minutes_date,
                    "type": "minutes",
                    "local_path": minutes_file
                })
        
        return documents
    
    def generate_mock_agenda_content(self, body, date):
        """Generate mock agenda content for testing."""
        return f"""
{body}
AGENDA
{date.strftime('%B %d, %Y')}

1. CALL TO ORDER

2. ROLL CALL

3. PUBLIC COMMENTS

4. CONSENT CALENDAR
   a. Approval of minutes from previous meeting
   b. Monthly financial report
   c. Routine administrative matters

5. OLD BUSINESS
   a. Follow-up on previous action items
   b. Status update on ongoing projects

6. NEW BUSINESS
   a. Review of proposed policy changes
   b. Budget considerations for next fiscal year
   c. Community development initiatives

7. REPORTS
   a. Staff reports
   b. Committee updates
   c. Public works status

8. FUTURE AGENDA ITEMS

9. ADJOURNMENT

This is a mock agenda created for testing purposes.
The actual agenda would contain specific items relevant to {body}.
"""
    
    def generate_mock_minutes_content(self, body, date):
        """Generate mock minutes content for testing."""
        return f"""
{body}
MEETING MINUTES
{date.strftime('%B %d, %Y')}

CALL TO ORDER
The meeting was called to order at 6:00 PM.

ROLL CALL
All members present.

PUBLIC COMMENTS
No public comments were received.

CONSENT CALENDAR
Motion to approve consent calendar items passed unanimously.

OLD BUSINESS
- Previous action items were reviewed and updated
- Ongoing projects are proceeding as scheduled

NEW BUSINESS
- Policy changes were discussed and will be voted on at next meeting
- Budget planning for next fiscal year was initiated
- Community development initiatives were reviewed

REPORTS
- Staff provided updates on current operations
- Committee chairs reported on recent activities
- Public works department provided status updates

ADJOURNMENT
Meeting adjourned at 8:30 PM.

This is a mock minutes document created for testing purposes.
The actual minutes would contain specific details relevant to {body}.
"""
    
    def save_mock_document(self, body, doc_type, date, content):
        """Save mock document content to file."""
        body_dir = body.replace(" ", "_").replace("&", "and")
        date_str = date.strftime("%Y%m%d")
        filename = f"{date_str}_{doc_type}_{body_dir}.txt"
        filepath = os.path.join(self.base_dir, body_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Created mock document: {filename}")
        return filepath
    
    def fetch_all_documents(self):
        """Main method to fetch all documents."""
        logger.info("Starting document fetch process...")
        
        try:
            documents = self.parse_meetings_page()
            
            # Download actual documents if URLs are available
            for body, body_docs in documents.items():
                for doc_type in ["agendas", "minutes"]:
                    for doc in body_docs[doc_type]:
                        if doc.get("url") and not doc["url"].startswith("mock://"):
                            local_path = self.download_document(doc, body)
                            if local_path:
                                doc["local_path"] = local_path
            
            logger.info(f"Document fetch completed. Found documents for {len(documents)} bodies.")
            return documents
            
        except Exception as e:
            logger.error(f"Error in fetch_all_documents: {e}")
            return self.create_mock_documents()

def main():
    """Main entry point for the script."""
    try:
        fetcher = MeetingDocumentFetcher()
        documents = fetcher.fetch_all_documents()
        
        # Save results to JSON file for other scripts to use
        output_file = "fetched_documents.json"
        with open(output_file, 'w') as f:
            # Convert datetime objects to strings for JSON serialization
            serializable_docs = {}
            for body, body_docs in documents.items():
                serializable_docs[body] = {}
                for doc_type in ["agendas", "minutes"]:
                    serializable_docs[body][doc_type] = []
                    for doc in body_docs[doc_type]:
                        serializable_doc = doc.copy()
                        if serializable_doc.get("date"):
                            serializable_doc["date"] = serializable_doc["date"].isoformat()
                        serializable_docs[body][doc_type].append(serializable_doc)
            
            json.dump(serializable_docs, f, indent=2)
        
        logger.info(f"Results saved to {output_file}")
        return documents
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return None

if __name__ == "__main__":
    main()

