#!/usr/bin/env python3
"""
La Canada Flintridge Government Meetings Tracker - Scheduler
Runs the complete workflow on a scheduled basis.
"""

import os
import sys
import json
import logging
import schedule
import time
import argparse
from datetime import datetime, timedelta

# Import our modules
import fetch_all_meetings
import summarize_all_meetings
import send_consolidated_email

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lcf_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LCFScheduler:
    """Scheduler for the La Canada Flintridge Government Tracker."""
    
    def __init__(self, config_path="config.json"):
        """Initialize the scheduler with configuration."""
        self.config_path = config_path
        self.config = self.load_config()
        self.last_run = None
        self.setup_schedule()
    
    def load_config(self):
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found. Using default settings.")
            return self.get_default_config()
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file {self.config_path}. Using default settings.")
            return self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration."""
        return {
            "schedule_day": "monday",
            "schedule_time": "08:00",
            "enabled_bodies": [
                "City Council",
                "Design Commission",
                "Investment & Financing Advisory Committee",
                "Parks & Recreation Commission",
                "Planning Commission",
                "Public Safety Commission",
                "Public Works and Traffic Commission",
                "Sustainability and Resilience Commission"
            ]
        }
    
    def setup_schedule(self):
        """Set up the scheduled job based on configuration."""
        schedule_day = self.config.get("schedule_day", "monday").lower()
        schedule_time = self.config.get("schedule_time", "08:00")
        
        # Map day names to schedule methods
        day_mapping = {
            "monday": schedule.every().monday,
            "tuesday": schedule.every().tuesday,
            "wednesday": schedule.every().wednesday,
            "thursday": schedule.every().thursday,
            "friday": schedule.every().friday,
            "saturday": schedule.every().saturday,
            "sunday": schedule.every().sunday
        }
        
        if schedule_day in day_mapping:
            day_mapping[schedule_day].at(schedule_time).do(self.run_workflow)
            logger.info(f"Scheduled to run every {schedule_day.title()} at {schedule_time}")
        else:
            logger.error(f"Invalid schedule day: {schedule_day}. Using Monday as default.")
            schedule.every().monday.at(schedule_time).do(self.run_workflow)
    
    def run_workflow(self):
        """Run the complete workflow: fetch, summarize, and email."""
        logger.info("="*60)
        logger.info("STARTING SCHEDULED LCF GOVERNMENT TRACKER WORKFLOW")
        logger.info("="*60)
        
        start_time = datetime.now()
        self.last_run = start_time
        
        try:
            # Step 1: Fetch documents
            logger.info("Step 1: Fetching meeting documents...")
            fetcher = fetch_all_meetings.MeetingDocumentFetcher(self.config_path)
            documents = fetcher.fetch_all_documents()
            
            if not documents:
                logger.error("Failed to fetch documents. Aborting workflow.")
                return False
            
            # Step 2: Generate summaries
            logger.info("Step 2: Generating document summaries...")
            summarizer = summarize_all_meetings.MeetingSummarizer(self.config_path)
            summaries = summarizer.summarize_all_documents(documents)
            
            if not summaries:
                logger.error("Failed to generate summaries. Aborting workflow.")
                return False
            
            # Step 3: Send email report
            logger.info("Step 3: Generating and sending email report...")
            reporter = send_consolidated_email.EmailReporter(self.config_path)
            success = reporter.generate_and_send_report(summaries)
            
            if not success:
                logger.error("Failed to generate/send email report.")
                return False
            
            # Calculate duration and log success
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info("="*60)
            logger.info("WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info(f"Duration: {duration.total_seconds():.2f} seconds")
            logger.info(f"Next run: {self.get_next_run_time()}")
            logger.info("="*60)
            
            return True
            
        except Exception as e:
            logger.error(f"Workflow failed with error: {e}")
            return False
    
    def get_next_run_time(self):
        """Get the next scheduled run time."""
        try:
            next_run = schedule.next_run()
            if next_run:
                return next_run.strftime("%A, %B %d, %Y at %I:%M %p")
            else:
                return "Not scheduled"
        except:
            return "Unknown"
    
    def get_status(self):
        """Get the current status of the scheduler."""
        status = {
            "scheduler_running": True,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.get_next_run_time(),
            "schedule_day": self.config.get("schedule_day", "monday"),
            "schedule_time": self.config.get("schedule_time", "08:00"),
            "enabled_bodies": self.config.get("enabled_bodies", [])
        }
        return status
    
    def run_scheduler(self, force_run=False):
        """Run the scheduler loop."""
        if force_run:
            logger.info("Force run requested - executing workflow immediately...")
            self.run_workflow()
            return
        
        logger.info("LCF Government Tracker Scheduler started")
        logger.info(f"Next scheduled run: {self.get_next_run_time()}")
        logger.info("Press Ctrl+C to stop the scheduler")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")

def main():
    """Main entry point for the scheduler script."""
    parser = argparse.ArgumentParser(description="La Canada Flintridge Government Tracker Scheduler")
    parser.add_argument("--force", action="store_true", help="Force run the workflow immediately")
    parser.add_argument("--status", action="store_true", help="Show scheduler status and exit")
    parser.add_argument("--config", default="config.json", help="Path to configuration file")
    
    args = parser.parse_args()
    
    try:
        scheduler = LCFScheduler(args.config)
        
        if args.status:
            status = scheduler.get_status()
            print("\nLCF Government Tracker Status:")
            print("-" * 40)
            print(f"Last run: {status['last_run'] or 'Never'}")
            print(f"Next run: {status['next_run']}")
            print(f"Schedule: Every {status['schedule_day'].title()} at {status['schedule_time']}")
            print(f"Tracking {len(status['enabled_bodies'])} government bodies")
            return
        
        scheduler.run_scheduler(force_run=args.force)
        
    except Exception as e:
        logger.error(f"Scheduler failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

