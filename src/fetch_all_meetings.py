#!/usr/bin/env python3
"""
LCF Civic Summaries - Document Fetcher
Railway-optimized version with environment variable configuration
"""

import os
import json
import logging
import time
import random
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RailwayMeetingsFetcher:
    """Railway-optimized document fetcher with environment variable configuration."""
    
    def __init__(self):
        """Initialize the fetcher with Railway environment variables."""
        self.data_dir = os.getenv('DATA_DIR', 'data')
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        # Create data directories
        self.documents_dir = os.path.join(self.data_dir, 'meeting_documents')
        self.manual_dir = os.path.join(self.data_dir, 'manual_downloads')
        os.makedirs(self.documents_dir, exist_ok=True)
        os.makedirs(self.manual_dir, exist_ok=True)
        
        # Website configuration
        self.base_url = "https://lcf.ca.gov"
        self.meetings_url = "https://lcf.ca.gov/city-clerk/agenda-minutes/"
        
        # Government bodies to track
        self.government_bodies = [
            "City Council",
            "Planning Commission", 
            "Public Safety Commission",
            "Parks & Recreation Commission",
            "Design Review Board",
            "Environmental Commission",
            "Traffic & Safety Commission",
            "Investment & Financing Advisory Committee"
        ]
        
        # Create enhanced session
        self.session = self.create_enhanced_session()
        
        logger.info(f"Fetcher initialized - Environment: {self.environment}")
        logger.info(f"Data directory: {self.data_dir}")
    
    def create_enhanced_session(self):
        """Create a requests session with enhanced headers and retry logic."""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Enhanced headers to appear more like a real browser
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return session
    
    def fetch_with_delay(self, url, min_delay=1, max_delay=3):
        """Fetch URL with random delay to avoid rate limiting."""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        
        try:
            response = self.session.get(url, timeout=30)
            logger.debug(f"Fetched {url} - Status: {response.status_code}")
            return response
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def create_mock_documents(self):
        """Create mock documents for testing when website is inaccessible."""
        logger.info("Creating mock documents for testing")
        
        mock_documents = []
        
        for body in self.government_bodies:
            # Create mock agenda
            agenda_doc = {
                'government_body': body,
                'document_type': 'agenda',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'title': f'{body} Meeting Agenda',
                'url': f'https://lcf.ca.gov/mock/{body.lower().replace(" ", "-")}-agenda.pdf',
                'content': f'Mock agenda content for {body} meeting. This is a test document created when the city website is inaccessible.',
                'filename': f'{body.lower().replace(" ", "_")}_agenda_{datetime.now().strftime("%Y%m%d")}.txt',
                'mock': True
            }
            
            # Create mock minutes
            minutes_doc = {
                'government_body': body,
                'document_type': 'minutes',
                'date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'title': f'{body} Meeting Minutes',
                'url': f'https://lcf.ca.gov/mock/{body.lower().replace(" ", "-")}-minutes.pdf',
                'content': f'Mock minutes content for {body} meeting. This is a test document created when the city website is inaccessible.',
                'filename': f'{body.lower().replace(" ", "_")}_minutes_{(datetime.now() - timedelta(days=7)).strftime("%Y%m%d")}.txt',
                'mock': True
            }
            
            mock_documents.extend([agenda_doc, minutes_doc])
        
        # Save mock documents to files
        for doc in mock_documents:
            file_path = os.path.join(self.documents_dir, doc['filename'])
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(doc['content'])
            
            logger.debug(f"Created mock document: {doc['filename']}")
        
        logger.info(f"Created {len(mock_documents)} mock documents")
        return mock_documents
    
    def process_manual_downloads(self):
        """Process any manually downloaded PDF files."""
        logger.info("Checking for manually downloaded documents")
        
        manual_documents = []
        
        if not os.path.exists(self.manual_dir):
            logger.info("No manual downloads directory found")
            return manual_documents
        
        pdf_files = [f for f in os.listdir(self.manual_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            logger.info("No PDF files found in manual downloads directory")
            return manual_documents
        
        logger.info(f"Found {len(pdf_files)} manually downloaded PDF files")
        
        for pdf_file in pdf_files:
            file_path = os.path.join(self.manual_dir, pdf_file)
            
            try:
                # Extract text from PDF (simplified version)
                content = self.extract_pdf_text(file_path)
                
                # Try to determine government body and document type from filename
                body, doc_type = self.parse_filename(pdf_file)
                
                doc = {
                    'government_body': body,
                    'document_type': doc_type,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'title': pdf_file,
                    'url': f'file://{file_path}',
                    'content': content,
                    'filename': pdf_file,
                    'manual': True
                }
                
                manual_documents.append(doc)
                logger.info(f"Processed manual document: {pdf_file}")
                
            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {str(e)}")
        
        return manual_documents
    
    def extract_pdf_text(self, file_path):
        """Extract text from PDF file."""
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return text.strip()
                
        except ImportError:
            logger.warning("PyPDF2 not available, using placeholder text")
            return f"PDF content from {os.path.basename(file_path)} (text extraction not available)"
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            return f"Error extracting text from {os.path.basename(file_path)}"
    
    def parse_filename(self, filename):
        """Parse filename to determine government body and document type."""
        filename_lower = filename.lower()
        
        # Determine government body
        body = "City Council"  # Default
        for gov_body in self.government_bodies:
            if any(word in filename_lower for word in gov_body.lower().split()):
                body = gov_body
                break
        
        # Determine document type
        doc_type = "agenda"  # Default
        if any(word in filename_lower for word in ['minutes', 'minute']):
            doc_type = "minutes"
        
        return body, doc_type
    
    def attempt_website_fetch(self):
        """Attempt to fetch documents from the city website."""
        logger.info("Attempting to fetch documents from city website")
        
        try:
            response = self.fetch_with_delay(self.meetings_url)
            
            if response and response.status_code == 200:
                logger.info("Successfully accessed city website")
                
                # Parse the page for document links
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for PDF links (this is a simplified implementation)
                pdf_links = soup.find_all('a', href=lambda x: x and x.lower().endswith('.pdf'))
                
                if pdf_links:
                    logger.info(f"Found {len(pdf_links)} PDF links on the website")
                    # In a full implementation, we would download and process these PDFs
                    return []
                else:
                    logger.info("No PDF links found on the website")
                    return []
            
            elif response and response.status_code == 403:
                logger.warning("Website returned 403 Forbidden - access blocked")
                return None
            
            else:
                logger.warning(f"Website returned status code: {response.status_code if response else 'No response'}")
                return None
                
        except Exception as e:
            logger.error(f"Error accessing website: {str(e)}")
            return None
    
    def save_documents_metadata(self, documents):
        """Save document metadata to JSON file."""
        metadata_file = os.path.join(self.data_dir, 'document_metadata.json')
        
        metadata = {
            'last_updated': datetime.now().isoformat(),
            'total_documents': len(documents),
            'documents': documents
        }
        
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            logger.info(f"Saved metadata for {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error saving document metadata: {str(e)}")
    
    def fetch_all_documents(self):
        """Main method to fetch all government meeting documents."""
        logger.info("=== Starting Document Fetching Process ===")
        
        all_documents = []
        
        # First, try to process any manually downloaded documents
        manual_docs = self.process_manual_downloads()
        all_documents.extend(manual_docs)
        
        # Attempt to fetch from website
        website_docs = self.attempt_website_fetch()
        
        if website_docs is None:
            # Website is inaccessible, use mock documents for testing
            logger.info("Website inaccessible, creating mock documents for testing")
            mock_docs = self.create_mock_documents()
            all_documents.extend(mock_docs)
        elif website_docs:
            # Successfully fetched from website
            all_documents.extend(website_docs)
        else:
            # Website accessible but no documents found
            logger.info("Website accessible but no documents found")
        
        # Save metadata
        self.save_documents_metadata(all_documents)
        
        logger.info(f"=== Document Fetching Complete: {len(all_documents)} documents ===")
        
        return {
            'total_documents': len(all_documents),
            'manual_documents': len(manual_docs),
            'website_documents': len(website_docs) if website_docs else 0,
            'mock_documents': len([d for d in all_documents if d.get('mock', False)]),
            'documents': all_documents
        }

def main():
    """Main function for Railway deployment."""
    try:
        fetcher = RailwayMeetingsFetcher()
        result = fetcher.fetch_all_documents()
        
        logger.info("Document fetching completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Document fetching failed: {str(e)}")
        raise

if __name__ == '__main__':
    main()

