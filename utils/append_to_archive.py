#!/usr/bin/env python3
"""
Append-Only Archive System for La Canada Flintridge Government Tracker
Appends new meeting summaries to the historical archive without duplicating existing data.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('append_archive.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ArchiveAppender:
    """Append new summaries to the historical archive system."""
    
    def __init__(self):
        """Initialize the archive appender."""
        self.current_summaries_file = "document_summaries.json"
        self.historical_summaries_dir = "historical_summaries_2025"
        self.historical_summaries_file = f"{self.historical_summaries_dir}/historical_summaries_2025.json"
        self.website_data_file = "website_data.json"
        
        # Create directories if they don't exist
        os.makedirs(self.historical_summaries_dir, exist_ok=True)
    
    def load_current_summaries(self):
        """Load the current week's summaries."""
        try:
            if not os.path.exists(self.current_summaries_file):
                logger.warning(f"⚠️ Current summaries file not found: {self.current_summaries_file}")
                return {}
            
            with open(self.current_summaries_file, 'r') as f:
                current_data = json.load(f)
            
            logger.info(f"✅ Loaded current summaries for {len(current_data)} government bodies")
            return current_data
            
        except Exception as e:
            logger.error(f"❌ Error loading current summaries: {e}")
            return {}
    
    def load_historical_archive(self):
        """Load the existing historical archive."""
        try:
            if not os.path.exists(self.historical_summaries_file):
                logger.info("📋 No existing historical archive found. Will create new one.")
                return {}
            
            with open(self.historical_summaries_file, 'r') as f:
                historical_data = json.load(f)
            
            logger.info(f"✅ Loaded historical archive for {len(historical_data)} government bodies")
            return historical_data
            
        except Exception as e:
            logger.error(f"❌ Error loading historical archive: {e}")
            return {}
    
    def is_duplicate_document(self, new_doc, existing_docs):
        """Check if a document already exists in the archive."""
        for existing_doc in existing_docs:
            # Check by title and date
            if (new_doc.get('title', '').strip() == existing_doc.get('title', '').strip() and
                new_doc.get('date', '') == existing_doc.get('date', '')):
                return True
            
            # Check by URL if available
            if (new_doc.get('url', '') and existing_doc.get('url', '') and
                new_doc['url'] == existing_doc['url']):
                return True
        
        return False
    
    def prepare_document_for_archive(self, doc, body_name):
        """Prepare a document for archival by adding necessary metadata."""
        archived_doc = doc.copy()
        
        # Add archive metadata
        archived_doc['archived_date'] = datetime.now().isoformat()
        archived_doc['historical'] = True
        
        # Ensure required fields exist
        if 'date' in archived_doc:
            try:
                doc_date = datetime.fromisoformat(archived_doc['date'].replace('Z', '+00:00'))
                archived_doc['month'] = doc_date.strftime('%B %Y')
                archived_doc['year'] = doc_date.year
            except:
                archived_doc['month'] = datetime.now().strftime('%B %Y')
                archived_doc['year'] = datetime.now().year
        
        # Ensure URL exists (create placeholder if missing)
        if 'url' not in archived_doc or not archived_doc['url']:
            doc_type = archived_doc.get('type', 'document')
            safe_title = archived_doc.get('title', '').replace(' ', '_').lower()
            archived_doc['url'] = f"https://lcf.ca.gov/{doc_type}s/{safe_title}.pdf"
        
        return archived_doc
    
    def append_to_archive(self, current_summaries, historical_archive):
        """Append new summaries to the historical archive."""
        logger.info("🔄 Appending new summaries to historical archive...")
        
        new_documents_added = 0
        updated_bodies = set()
        
        for body_name, body_data in current_summaries.items():
            # Initialize body in historical archive if it doesn't exist
            if body_name not in historical_archive:
                historical_archive[body_name] = {"agendas": [], "minutes": []}
                logger.info(f"📋 Created new archive section for {body_name}")
            
            # Process agendas
            for agenda in body_data.get('agendas', []):
                if not self.is_duplicate_document(agenda, historical_archive[body_name]['agendas']):
                    archived_agenda = self.prepare_document_for_archive(agenda, body_name)
                    historical_archive[body_name]['agendas'].append(archived_agenda)
                    new_documents_added += 1
                    updated_bodies.add(body_name)
                    logger.info(f"➕ Added new agenda: {agenda.get('title', 'Untitled')}")
                else:
                    logger.info(f"⏭️ Skipped duplicate agenda: {agenda.get('title', 'Untitled')}")
            
            # Process minutes
            for minutes in body_data.get('minutes', []):
                if not self.is_duplicate_document(minutes, historical_archive[body_name]['minutes']):
                    archived_minutes = self.prepare_document_for_archive(minutes, body_name)
                    historical_archive[body_name]['minutes'].append(archived_minutes)
                    new_documents_added += 1
                    updated_bodies.add(body_name)
                    logger.info(f"➕ Added new minutes: {minutes.get('title', 'Untitled')}")
                else:
                    logger.info(f"⏭️ Skipped duplicate minutes: {minutes.get('title', 'Untitled')}")
        
        logger.info(f"✅ Archive update complete:")
        logger.info(f"   📄 New documents added: {new_documents_added}")
        logger.info(f"   🏛️ Government bodies updated: {len(updated_bodies)}")
        
        return historical_archive, new_documents_added, updated_bodies
    
    def sort_archive_documents(self, historical_archive):
        """Sort all documents in the archive by date (newest first)."""
        for body_name, body_data in historical_archive.items():
            # Sort agendas by date
            body_data['agendas'].sort(
                key=lambda x: x.get('date', ''), 
                reverse=True
            )
            
            # Sort minutes by date
            body_data['minutes'].sort(
                key=lambda x: x.get('date', ''), 
                reverse=True
            )
        
        logger.info("📅 Sorted all archive documents by date")
    
    def save_updated_archive(self, historical_archive):
        """Save the updated historical archive."""
        try:
            # Sort documents before saving
            self.sort_archive_documents(historical_archive)
            
            # Save main historical archive
            with open(self.historical_summaries_file, 'w') as f:
                json.dump(historical_archive, f, indent=2, default=str)
            
            # Update archive statistics
            stats = self.calculate_archive_stats(historical_archive)
            stats_file = f"{self.historical_summaries_dir}/archive_stats.json"
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
            
            # Create monthly breakdown files
            self.create_monthly_files(historical_archive)
            
            logger.info(f"✅ Updated historical archive saved to {self.historical_summaries_file}")
            logger.info(f"📊 Archive statistics: {stats['total_documents']} total documents")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving updated archive: {e}")
            return False
    
    def calculate_archive_stats(self, historical_archive):
        """Calculate statistics for the historical archive."""
        stats = {
            "last_updated": datetime.now().isoformat(),
            "total_government_bodies": len(historical_archive),
            "total_documents": 0,
            "total_agendas": 0,
            "total_minutes": 0,
            "ai_generated_count": 0,
            "months_covered": set(),
            "years_covered": set(),
            "government_bodies": list(historical_archive.keys())
        }
        
        for body_name, body_data in historical_archive.items():
            # Count agendas
            agendas = body_data.get('agendas', [])
            stats['total_agendas'] += len(agendas)
            stats['total_documents'] += len(agendas)
            
            for agenda in agendas:
                if agenda.get('ai_generated', False):
                    stats['ai_generated_count'] += 1
                if 'month' in agenda:
                    stats['months_covered'].add(agenda['month'])
                if 'year' in agenda:
                    stats['years_covered'].add(str(agenda['year']))
            
            # Count minutes
            minutes = body_data.get('minutes', [])
            stats['total_minutes'] += len(minutes)
            stats['total_documents'] += len(minutes)
            
            for minute in minutes:
                if minute.get('ai_generated', False):
                    stats['ai_generated_count'] += 1
                if 'month' in minute:
                    stats['months_covered'].add(minute['month'])
                if 'year' in minute:
                    stats['years_covered'].add(str(minute['year']))
        
        # Convert sets to sorted lists
        stats['months_covered'] = sorted(list(stats['months_covered']))
        stats['years_covered'] = sorted(list(stats['years_covered']))
        
        return stats
    
    def create_monthly_files(self, historical_archive):
        """Create separate files for each month's data."""
        monthly_data = {}
        
        # Group documents by month
        for body_name, body_data in historical_archive.items():
            for doc_type in ['agendas', 'minutes']:
                for doc in body_data.get(doc_type, []):
                    month = doc.get('month', 'Unknown')
                    if month not in monthly_data:
                        monthly_data[month] = {}
                    if body_name not in monthly_data[month]:
                        monthly_data[month][body_name] = {'agendas': [], 'minutes': []}
                    monthly_data[month][body_name][doc_type].append(doc)
        
        # Save monthly files
        for month, month_data in monthly_data.items():
            safe_month = month.replace(' ', '_').lower()
            month_file = f"{self.historical_summaries_dir}/month_{safe_month}.json"
            with open(month_file, 'w') as f:
                json.dump(month_data, f, indent=2, default=str)
        
        logger.info(f"📅 Created {len(monthly_data)} monthly archive files")
    
    def update_website_data(self, historical_archive):
        """Update the website data file with combined current and historical data."""
        try:
            # Load current website data
            current_website_data = {}
            if os.path.exists(self.website_data_file):
                with open(self.website_data_file, 'r') as f:
                    current_website_data = json.load(f)
            
            # Create combined data structure for website
            combined_data = {
                "current_summaries": current_website_data,
                "historical_archive": historical_archive,
                "last_updated": datetime.now().isoformat(),
                "archive_enabled": True
            }
            
            # Save combined data
            combined_file = "combined_website_data.json"
            with open(combined_file, 'w') as f:
                json.dump(combined_data, f, indent=2, default=str)
            
            logger.info(f"✅ Updated website data with historical archive")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating website data: {e}")
            return False

def main():
    """Main entry point for archive appending."""
    try:
        logger.info("🏛️ Starting Archive Append Process...")
        
        appender = ArchiveAppender()
        
        # Load current summaries
        current_summaries = appender.load_current_summaries()
        if not current_summaries:
            logger.warning("⚠️ No current summaries to append. Exiting.")
            return True
        
        # Load historical archive
        historical_archive = appender.load_historical_archive()
        
        # Append new summaries
        updated_archive, new_docs, updated_bodies = appender.append_to_archive(
            current_summaries, historical_archive
        )
        
        if new_docs > 0:
            # Save updated archive
            if appender.save_updated_archive(updated_archive):
                # Update website data
                appender.update_website_data(updated_archive)
                
                logger.info("✅ Archive append process completed successfully!")
                logger.info(f"📈 Summary: {new_docs} new documents added to archive")
                logger.info(f"🏛️ Updated bodies: {', '.join(updated_bodies)}")
                return True
            else:
                logger.error("❌ Failed to save updated archive")
                return False
        else:
            logger.info("ℹ️ No new documents to add to archive")
            return True
        
    except Exception as e:
        logger.error(f"❌ Error in archive append process: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

