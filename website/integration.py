#!/usr/bin/env python3
"""
Integration script to connect LCF Civic Summaries website with the existing tracker system.
This script will be called by the tracker system to update the website data.
"""

import json
import os
import shutil
from datetime import datetime
from flask import Blueprint

integration_bp = Blueprint('integration', __name__)

class TrackerIntegration:
    def __init__(self):
        self.tracker_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'lcf-tracker-github')
        self.website_data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        # Ensure data directory exists
        os.makedirs(self.website_data_dir, exist_ok=True)
    
    def update_website_data(self):
        """Update website data from the tracker system."""
        try:
            # Path to the tracker's summary file
            tracker_summaries = os.path.join(self.tracker_dir, 'document_summaries.json')
            
            if not os.path.exists(tracker_summaries):
                print(f"Tracker summaries file not found: {tracker_summaries}")
                return False
            
            # Load tracker data
            with open(tracker_summaries, 'r') as f:
                tracker_data = json.load(f)
            
            # Transform data for website format
            website_data = self.transform_tracker_data(tracker_data)
            
            # Save to website data directory
            website_summaries = os.path.join(self.website_data_dir, 'summaries.json')
            with open(website_summaries, 'w') as f:
                json.dump(website_data, f, indent=2, default=str)
            
            # Update metadata
            metadata = {
                "last_updated": datetime.now().isoformat(),
                "source": "lcf-tracker-github",
                "total_documents": self.count_documents(website_data),
                "government_bodies": list(website_data.keys())
            }
            
            metadata_file = os.path.join(self.website_data_dir, 'metadata.json')
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"Website data updated successfully at {datetime.now()}")
            return True
            
        except Exception as e:
            print(f"Error updating website data: {e}")
            return False
    
    def transform_tracker_data(self, tracker_data):
        """Transform tracker data format to website format."""
        website_data = {}
        
        for body_name, body_data in tracker_data.items():
            website_data[body_name] = {
                "agendas": [],
                "minutes": []
            }
            
            # Process agendas
            if "agendas" in body_data:
                for agenda in body_data["agendas"]:
                    website_data[body_name]["agendas"].append({
                        "title": agenda.get("title", "Meeting Agenda"),
                        "type": "agenda",
                        "date": agenda.get("date", ""),
                        "summary": agenda.get("summary", "No summary available."),
                        "ai_generated": agenda.get("ai_generated", False),
                        "url": agenda.get("url", "")
                    })
            
            # Process minutes
            if "minutes" in body_data:
                for minute in body_data["minutes"]:
                    website_data[body_name]["minutes"].append({
                        "title": minute.get("title", "Meeting Minutes"),
                        "type": "minutes",
                        "date": minute.get("date", ""),
                        "summary": minute.get("summary", "No summary available."),
                        "ai_generated": minute.get("ai_generated", False),
                        "url": minute.get("url", "")
                    })
        
        return website_data
    
    def count_documents(self, data):
        """Count total documents in the data."""
        total = 0
        for body_data in data.values():
            total += len(body_data.get("agendas", []))
            total += len(body_data.get("minutes", []))
        return total
    
    def get_historical_archive(self):
        """Get historical archive data from the tracker system."""
        try:
            # Try to load historical summaries from the tracker system
            historical_file = os.path.join(self.tracker_dir, "historical_summaries_2025", "historical_summaries_2025.json")
            
            if os.path.exists(historical_file):
                with open(historical_file, 'r') as f:
                    historical_data = json.load(f)
                
                # Load archive statistics
                stats_file = os.path.join(self.tracker_dir, "historical_summaries_2025", "archive_stats.json")
                metadata = {}
                if os.path.exists(stats_file):
                    with open(stats_file, 'r') as f:
                        metadata = json.load(f)
                
                return {
                    "success": True,
                    "data": historical_data,
                    "metadata": metadata
                }
            else:
                return {
                    "success": False,
                    "error": "Historical archive not found",
                    "data": {}
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error loading historical archive: {str(e)}",
                "data": {}
            }

    def get_website_data(self):
        """Get current website data."""
        try:
            summaries_file = os.path.join(self.website_data_dir, 'summaries.json')
            metadata_file = os.path.join(self.website_data_dir, 'metadata.json')
            
            if os.path.exists(summaries_file):
                with open(summaries_file, 'r') as f:
                    summaries = json.load(f)
                
                metadata = {}
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                
                return {
                    "success": True,
                    "data": summaries,
                    "metadata": metadata
                }
            else:
                return {
                    "success": False,
                    "error": "No website data available"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

@integration_bp.route('/update', methods=['POST'])
def update_data():
    """API endpoint to trigger data update."""
    integration = TrackerIntegration()
    success = integration.update_website_data()
    
    if success:
        return {"success": True, "message": "Website data updated successfully"}
    else:
        return {"success": False, "message": "Failed to update website data"}, 500

def main():
    """Main function for standalone execution."""
    integration = TrackerIntegration()
    success = integration.update_website_data()
    
    if success:
        print("✅ Website data updated successfully!")
    else:
        print("❌ Failed to update website data")
        exit(1)

if __name__ == "__main__":
    main()

