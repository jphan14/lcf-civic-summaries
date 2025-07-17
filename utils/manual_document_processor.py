#!/usr/bin/env python3
"""
Manual Document Processor for La Canada Flintridge Government Tracker
Processes manually downloaded documents and integrates them into the tracker system.
"""

import os
import sys
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
import PyPDF2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('manual_document_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ManualDocumentProcessor:
    """Process manually downloaded documents for the tracker system."""
    
    def __init__(self):
        """Initialize the processor."""
        self.docs_dir = "meeting_documents"
        self.manual_dir = "manual_downloads"
        self.processed_dir = "processed_documents"
        
        # Create directories
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.manual_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # Government bodies mapping
        self.government_bodies = {
            "city_council": "City Council",
            "planning": "Planning Commission",
            "public_safety": "Public Safety Commission", 
            "parks_rec": "Parks & Recreation Commission",
            "design": "Design Review Board",
            "environmental": "Environmental Commission",
            "traffic": "Traffic & Safety Commission",
            "tree": "Tree Advisory Committee"
        }
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text content from a PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                return text.strip()
                
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return None
    
    def detect_document_info(self, filename, content=None):
        """Detect document type and government body from filename and content."""
        filename_lower = filename.lower()
        
        # Detect document type
        doc_type = "unknown"
        if "agenda" in filename_lower:
            doc_type = "agenda"
        elif "minute" in filename_lower:
            doc_type = "minutes"
        
        # Detect government body
        body = "Unknown"
        for key, full_name in self.government_bodies.items():
            if key in filename_lower or full_name.lower().replace(' ', '').replace('&', '') in filename_lower.replace(' ', '').replace('&', ''):
                body = full_name
                break
        
        # Try to detect from content if available
        if content and body == "Unknown":
            content_lower = content.lower()
            for key, full_name in self.government_bodies.items():
                if full_name.lower() in content_lower:
                    body = full_name
                    break
        
        return doc_type, body
    
    def process_manual_documents(self):
        """Process all documents in the manual downloads folder."""
        logger.info("🔄 Processing manually downloaded documents...")
        
        manual_path = Path(self.manual_dir)
        if not manual_path.exists():
            logger.info(f"📁 Manual downloads directory not found: {self.manual_dir}")
            logger.info("📋 To use manual processing:")
            logger.info("   1. Create a 'manual_downloads' folder")
            logger.info("   2. Download PDFs from https://lcf.ca.gov/city-clerk/agenda-minutes/")
            logger.info("   3. Place them in the manual_downloads folder")
            logger.info("   4. Run this script again")
            return {}
        
        # Find all PDF files
        pdf_files = list(manual_path.glob("*.pdf"))
        
        if not pdf_files:
            logger.info("📄 No PDF files found in manual_downloads folder")
            return {}
        
        logger.info(f"📄 Found {len(pdf_files)} PDF files to process")
        
        # Initialize documents data structure
        documents_data = {}
        for body in self.government_bodies.values():
            documents_data[body] = {
                "agendas": [],
                "minutes": []
            }
        
        # Process each PDF
        for pdf_file in pdf_files:
            try:
                logger.info(f"📖 Processing: {pdf_file.name}")
                
                # Extract text content
                content = self.extract_text_from_pdf(pdf_file)
                
                # Detect document info
                doc_type, body = self.detect_document_info(pdf_file.name, content)
                
                if body == "Unknown":
                    logger.warning(f"⚠️  Could not determine government body for: {pdf_file.name}")
                    continue
                
                # Create organized directory structure
                body_dir = os.path.join(self.docs_dir, body.replace(' ', '_').replace('&', 'and'))
                os.makedirs(body_dir, exist_ok=True)
                
                # Generate organized filename
                timestamp = datetime.now().strftime("%Y%m%d")
                organized_filename = f"{timestamp}_{doc_type}_{body.replace(' ', '_').replace('&', 'and')}.pdf"
                organized_path = os.path.join(body_dir, organized_filename)
                
                # Copy file to organized location
                shutil.copy2(pdf_file, organized_path)
                
                # Create document entry
                doc_entry = {
                    "title": f"{body} {doc_type.title()} - {datetime.now().strftime('%B %d, %Y')}",
                    "date": datetime.now().isoformat(),
                    "local_path": organized_path,
                    "url": f"manual://{pdf_file.name}",
                    "type": doc_type,
                    "text_content": content
                }
                
                # Add to appropriate category
                if doc_type == "agenda":
                    documents_data[body]["agendas"].append(doc_entry)
                elif doc_type == "minutes":
                    documents_data[body]["minutes"].append(doc_entry)
                
                # Move processed file
                processed_path = os.path.join(self.processed_dir, pdf_file.name)
                shutil.move(pdf_file, processed_path)
                
                logger.info(f"✅ Processed: {pdf_file.name} → {body} ({doc_type})")
                
            except Exception as e:
                logger.error(f"❌ Error processing {pdf_file.name}: {e}")
        
        # Save documents data
        with open("documents_data.json", 'w') as f:
            json.dump(documents_data, f, indent=2, default=str)
        
        # Count processed documents
        total_docs = 0
        for body_data in documents_data.values():
            total_docs += len(body_data.get("agendas", []))
            total_docs += len(body_data.get("minutes", []))
        
        logger.info(f"🎉 Manual processing completed! Processed {total_docs} documents")
        
        return documents_data
    
    def create_download_guide(self):
        """Create a guide for manually downloading documents."""
        guide_content = """# Manual Document Download Guide

## 📋 How to Download La Cañada Flintridge Meeting Documents

### Step 1: Visit the City Website
Go to: https://lcf.ca.gov/city-clerk/agenda-minutes/

### Step 2: Download Documents
1. Look for recent meeting agendas and minutes
2. Right-click on PDF links and select "Save Link As..."
3. Save files to the `manual_downloads` folder

### Step 3: File Naming (Optional but Helpful)
For best results, include keywords in filenames:
- `city_council_agenda_2025.pdf`
- `planning_commission_minutes_2025.pdf`
- `public_safety_agenda_2025.pdf`

### Step 4: Process Documents
Run: `python3 manual_document_processor.py`

## 🏛️ Government Bodies to Look For:
- City Council
- Planning Commission
- Public Safety Commission
- Parks & Recreation Commission
- Design Review Board
- Environmental Commission
- Traffic & Safety Commission
- Tree Advisory Committee

## 📁 Folder Structure:
```
manual_downloads/          ← Place downloaded PDFs here
meeting_documents/         ← Organized documents (auto-created)
processed_documents/       ← Processed files (auto-created)
```

## 🔄 Automation:
Once documents are processed, your tracker system will:
1. ✅ Generate AI summaries
2. ✅ Update the website
3. ✅ Send email reports (if configured)

## 💡 Tips:
- Download 2-3 recent meetings per body
- Check the website weekly for new documents
- The system will handle duplicates automatically
"""
        
        with open("MANUAL_DOWNLOAD_GUIDE.md", 'w') as f:
            f.write(guide_content)
        
        logger.info("📖 Created MANUAL_DOWNLOAD_GUIDE.md")

def main():
    """Main entry point for manual document processing."""
    try:
        processor = ManualDocumentProcessor()
        
        # Create download guide
        processor.create_download_guide()
        
        # Process any existing documents
        documents = processor.process_manual_documents()
        
        if documents:
            # Check if any documents were actually processed
            total_docs = sum(len(body_data.get("agendas", [])) + len(body_data.get("minutes", [])) 
                           for body_data in documents.values())
            
            if total_docs > 0:
                logger.info("✅ Manual document processing completed successfully")
                logger.info("🔄 You can now run the summarizer and email reporter:")
                logger.info("   python3 summarize_all_meetings.py")
                logger.info("   python3 send_consolidated_email.py")
                return True
            else:
                logger.info("📋 No documents processed. See MANUAL_DOWNLOAD_GUIDE.md for instructions.")
                return True
        else:
            logger.info("📋 Manual processing setup complete. See MANUAL_DOWNLOAD_GUIDE.md for instructions.")
            return True
            
    except Exception as e:
        logger.error(f"Error in manual processing: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

