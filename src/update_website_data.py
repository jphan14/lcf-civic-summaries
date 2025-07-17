#!/usr/bin/env python3
"""
LCF Civic Summaries - Website Data Updater
Railway-optimized version for updating website data files
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RailwayWebsiteUpdater:
    """Railway-optimized website data updater."""
    
    def __init__(self):
        """Initialize the website updater with Railway environment variables."""
        self.data_dir = os.getenv('DATA_DIR', 'data')
        self.environment = os.getenv('ENVIRONMENT', 'production')
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        logger.info(f"Website updater initialized - Environment: {self.environment}")
    
    def load_json_file(self, filename: str, default=None) -> Dict[str, Any]:
        """Load JSON file with error handling."""
        file_path = os.path.join(self.data_dir, filename)
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"File not found: {file_path}")
                return default or {}
        except Exception as e:
            logger.error(f"Error loading {filename}: {str(e)}")
            return default or {}
    
    def save_json_file(self, filename: str, data: Dict[str, Any]) -> bool:
        """Save JSON file with error handling."""
        file_path = os.path.join(self.data_dir, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Saved data to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving {filename}: {str(e)}")
            return False
    
    def load_summaries(self) -> List[Dict[str, Any]]:
        """Load document summaries."""
        summaries_data = self.load_json_file('document_summaries.json', {})
        return summaries_data.get('summaries', [])
    
    def load_historical_archive(self) -> List[Dict[str, Any]]:
        """Load historical archive data."""
        archive_data = self.load_json_file('historical_summaries_2025.json', {})
        return archive_data.get('summaries', [])
    
    def organize_summaries_by_type(self, summaries: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Organize summaries by document type (agenda vs minutes)."""
        organized = {
            'agendas': [],
            'minutes': []
        }
        
        for summary in summaries:
            doc_type = summary.get('document_type', 'agenda')
            if doc_type == 'minutes':
                organized['minutes'].append(summary)
            else:
                organized['agendas'].append(summary)
        
        return organized
    
    def calculate_statistics(self, summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics for summaries."""
        if not summaries:
            return {
                'total_documents': 0,
                'government_bodies': 0,
                'ai_summaries': 0,
                'recent_updates': 0
            }
        
        # Count unique government bodies
        government_bodies = set(s.get('government_body', '') for s in summaries)
        
        # Count AI-generated summaries
        ai_summaries = len([s for s in summaries if s.get('ai_generated', False)])
        
        # Count recent updates (last 30 days)
        recent_count = 0
        try:
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=30)
            
            for summary in summaries:
                created_at = summary.get('created_at', '')
                if created_at:
                    try:
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if created_date > cutoff_date:
                            recent_count += 1
                    except:
                        pass
        except:
            pass
        
        return {
            'total_documents': len(summaries),
            'government_bodies': len(government_bodies),
            'ai_summaries': ai_summaries,
            'recent_updates': recent_count
        }
    
    def create_website_data(self) -> Dict[str, Any]:
        """Create website data structure for current summaries."""
        logger.info("Creating website data for current summaries")
        
        summaries = self.load_summaries()
        organized = self.organize_summaries_by_type(summaries)
        statistics = self.calculate_statistics(summaries)
        
        website_data = {
            'last_updated': datetime.now().isoformat(),
            'statistics': statistics,
            'summaries': summaries,
            'agendas': organized['agendas'],
            'minutes': organized['minutes']
        }
        
        return website_data
    
    def create_combined_data(self) -> Dict[str, Any]:
        """Create combined data structure with current and historical summaries."""
        logger.info("Creating combined data with historical archive")
        
        current_summaries = self.load_summaries()
        historical_summaries = self.load_historical_archive()
        
        # Organize historical data by month
        monthly_archive = {}
        for summary in historical_summaries:
            # Extract month from date or created_at
            month_key = "Unknown Month"
            
            date_str = summary.get('date', summary.get('created_at', ''))
            if date_str:
                try:
                    if 'T' in date_str:  # ISO format
                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:  # Simple date format
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    month_key = date_obj.strftime('%B %Y')
                except:
                    pass
            
            if month_key not in monthly_archive:
                monthly_archive[month_key] = []
            
            monthly_archive[month_key].append(summary)
        
        # Calculate combined statistics
        all_summaries = current_summaries + historical_summaries
        combined_statistics = self.calculate_statistics(all_summaries)
        
        combined_data = {
            'last_updated': datetime.now().isoformat(),
            'statistics': combined_statistics,
            'current_summaries': current_summaries,
            'archive_summaries': historical_summaries,
            'monthly_archive': monthly_archive
        }
        
        return combined_data
    
    def update_all_website_data(self):
        """Update all website data files."""
        logger.info("=== Starting Website Data Update ===")
        
        try:
            # Create current website data
            website_data = self.create_website_data()
            success1 = self.save_json_file('website_data.json', website_data)
            
            # Create combined data with archive
            combined_data = self.create_combined_data()
            success2 = self.save_json_file('combined_website_data.json', combined_data)
            
            if success1 and success2:
                logger.info("=== Website Data Update Complete ===")
                logger.info(f"Current summaries: {len(website_data.get('summaries', []))}")
                logger.info(f"Historical summaries: {len(combined_data.get('archive_summaries', []))}")
                
                return {
                    'status': 'success',
                    'current_summaries': len(website_data.get('summaries', [])),
                    'historical_summaries': len(combined_data.get('archive_summaries', [])),
                    'files_updated': ['website_data.json', 'combined_website_data.json']
                }
            else:
                logger.error("Failed to save website data files")
                return {
                    'status': 'error',
                    'message': 'Failed to save website data files'
                }
                
        except Exception as e:
            logger.error(f"Error updating website data: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

def main():
    """Main function for Railway deployment."""
    try:
        updater = RailwayWebsiteUpdater()
        result = updater.update_all_website_data()
        
        if result['status'] == 'success':
            logger.info("Website data update completed successfully")
        else:
            logger.error(f"Website data update failed: {result.get('message', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Website data update failed: {str(e)}")
        raise

if __name__ == '__main__':
    main()

