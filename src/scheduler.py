#!/usr/bin/env python3
"""
LCF Civic Summaries Scheduler
Railway-optimized version with environment variable configuration
"""

import os
import sys
import time
import schedule
import logging
import traceback
from datetime import datetime, timedelta
from functools import wraps

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RailwayConfig:
    """Configuration from environment variables"""
    
    def __init__(self):
        # Schedule configuration
        self.schedule_time = os.getenv('SCHEDULE_TIME', '09:00')
        self.schedule_day = os.getenv('SCHEDULE_DAY', 'monday').lower()
        self.timezone = os.getenv('TIMEZONE', 'America/Los_Angeles')
        
        # Processing configuration
        self.data_dir = os.getenv('DATA_DIR', 'data')
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        # API configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.max_tokens = int(os.getenv('MAX_TOKENS', '1000'))
        
        # Email configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.email_from = os.getenv('EMAIL_FROM')
        self.email_to = os.getenv('EMAIL_TO')
        self.send_email = os.getenv('SEND_EMAIL', 'true').lower() == 'true'
        
        # Alerting configuration
        self.alert_webhook_url = os.getenv('ALERT_WEBHOOK_URL')
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        logger.info(f"Scheduler configured - Day: {self.schedule_day}, Time: {self.schedule_time}")
        logger.info(f"Environment: {self.environment}, Data dir: {self.data_dir}")

config = RailwayConfig()

def send_alert(message, severity="info"):
    """Send alert notification via webhook"""
    if not config.alert_webhook_url:
        logger.info(f"Alert [{severity.upper()}]: {message}")
        return
    
    try:
        import requests
        payload = {
            "text": f"LCF Civic Summaries [{severity.upper()}]: {message}",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": config.environment
        }
        
        response = requests.post(
            config.alert_webhook_url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"Alert sent successfully: {message}")
        else:
            logger.warning(f"Alert webhook returned {response.status_code}")
            
    except Exception as e:
        logger.error(f"Failed to send alert: {str(e)}")

def retry_on_failure(max_retries=3, delay=60):
    """Decorator to retry functions on failure with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Function {func.__name__} failed after {max_retries} attempts: {str(e)}")
                        send_alert(f"Function {func.__name__} failed permanently: {str(e)}", "error")
                        raise
                    else:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Function {func.__name__} failed on attempt {attempt + 1}, retrying in {wait_time} seconds: {str(e)}")
                        time.sleep(wait_time)
            return None
        return wrapper
    return decorator

def safe_job_execution(job_func):
    """Wrapper for safe job execution with comprehensive error handling"""
    @wraps(job_func)
    def wrapper():
        job_start_time = datetime.utcnow()
        logger.info(f"Starting job: {job_func.__name__} at {job_start_time.isoformat()}")
        
        try:
            result = job_func()
            
            job_end_time = datetime.utcnow()
            duration = (job_end_time - job_start_time).total_seconds()
            
            logger.info(f"Job completed successfully: {job_func.__name__} (duration: {duration:.2f}s)")
            send_alert(f"Job {job_func.__name__} completed successfully in {duration:.2f}s", "info")
            
            return result
            
        except Exception as e:
            job_end_time = datetime.utcnow()
            duration = (job_end_time - job_start_time).total_seconds()
            
            logger.error(f"Job failed: {job_func.__name__} (duration: {duration:.2f}s)")
            logger.error(f"Error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            send_alert(f"Job {job_func.__name__} failed after {duration:.2f}s: {str(e)}", "error")
            
            # Don't re-raise to prevent scheduler from stopping
            return None
    return wrapper

@retry_on_failure(max_retries=3, delay=120)
def fetch_documents():
    """Fetch government meeting documents"""
    logger.info("Starting document fetching process")
    
    try:
        # Import the fetch module
        from fetch_all_meetings_enhanced import main as fetch_main
        
        # Run the fetching process
        result = fetch_main()
        
        logger.info("Document fetching completed successfully")
        return result
        
    except ImportError:
        logger.warning("Enhanced fetcher not available, using standard fetcher")
        try:
            from fetch_all_meetings import main as fetch_main
            result = fetch_main()
            logger.info("Document fetching completed with standard fetcher")
            return result
        except ImportError:
            logger.error("No document fetcher available")
            raise

@retry_on_failure(max_retries=3, delay=120)
def generate_summaries():
    """Generate AI summaries of documents"""
    logger.info("Starting AI summarization process")
    
    if not config.openai_api_key:
        logger.warning("OpenAI API key not configured, skipping AI summarization")
        return None
    
    try:
        # Import the summarization module
        from summarize_all_meetings_optimized import main as summarize_main
        
        # Run the summarization process
        result = summarize_main()
        
        logger.info("AI summarization completed successfully")
        return result
        
    except ImportError:
        logger.warning("Optimized summarizer not available, using standard summarizer")
        try:
            from summarize_all_meetings import main as summarize_main
            result = summarize_main()
            logger.info("AI summarization completed with standard summarizer")
            return result
        except ImportError:
            logger.error("No summarizer available")
            raise

@retry_on_failure(max_retries=3, delay=60)
def send_email_report():
    """Send consolidated email report"""
    logger.info("Starting email report generation")
    
    if not config.send_email:
        logger.info("Email sending disabled in configuration")
        return None
    
    if not all([config.smtp_username, config.smtp_password, config.email_from, config.email_to]):
        logger.warning("Email configuration incomplete, skipping email sending")
        return None
    
    try:
        # Import the email module
        from send_consolidated_email import main as email_main
        
        # Run the email process
        result = email_main()
        
        logger.info("Email report sent successfully")
        return result
        
    except ImportError:
        logger.error("Email module not available")
        raise

@retry_on_failure(max_retries=2, delay=30)
def update_website_data():
    """Update website data files"""
    logger.info("Starting website data update")
    
    try:
        # Import the website update module
        from update_website_standalone import main as update_main
        
        # Run the update process
        result = update_main()
        
        logger.info("Website data updated successfully")
        return result
        
    except ImportError:
        logger.warning("Website update module not available")
        return None

@retry_on_failure(max_retries=2, delay=30)
def update_historical_archive():
    """Update historical archive with new data"""
    logger.info("Starting historical archive update")
    
    try:
        # Import the archive update module
        from append_to_archive import main as archive_main
        
        # Run the archive update process
        result = archive_main()
        
        logger.info("Historical archive updated successfully")
        return result
        
    except ImportError:
        logger.warning("Archive update module not available")
        return None

@safe_job_execution
def run_weekly_processing():
    """Execute the complete weekly government document processing pipeline"""
    logger.info("=== Starting Weekly LCF Government Document Processing ===")
    
    pipeline_start_time = datetime.utcnow()
    
    try:
        # Step 1: Fetch documents
        logger.info("Step 1: Fetching government documents")
        fetch_result = fetch_documents()
        
        # Step 2: Generate AI summaries
        logger.info("Step 2: Generating AI summaries")
        summary_result = generate_summaries()
        
        # Step 3: Update website data
        logger.info("Step 3: Updating website data")
        website_result = update_website_data()
        
        # Step 4: Update historical archive
        logger.info("Step 4: Updating historical archive")
        archive_result = update_historical_archive()
        
        # Step 5: Send email report
        logger.info("Step 5: Sending email report")
        email_result = send_email_report()
        
        pipeline_end_time = datetime.utcnow()
        total_duration = (pipeline_end_time - pipeline_start_time).total_seconds()
        
        logger.info(f"=== Weekly Processing Completed Successfully ===")
        logger.info(f"Total processing time: {total_duration:.2f} seconds")
        
        # Send success notification
        send_alert(f"Weekly processing completed successfully in {total_duration:.2f}s", "info")
        
        return {
            'status': 'success',
            'duration': total_duration,
            'steps': {
                'fetch': fetch_result is not None,
                'summarize': summary_result is not None,
                'website': website_result is not None,
                'archive': archive_result is not None,
                'email': email_result is not None
            }
        }
        
    except Exception as e:
        pipeline_end_time = datetime.utcnow()
        total_duration = (pipeline_end_time - pipeline_start_time).total_seconds()
        
        logger.error(f"=== Weekly Processing Failed ===")
        logger.error(f"Error after {total_duration:.2f} seconds: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        send_alert(f"Weekly processing failed after {total_duration:.2f}s: {str(e)}", "error")
        
        raise

def configure_schedule():
    """Configure the weekly schedule based on environment variables"""
    logger.info(f"Configuring schedule for {config.schedule_day} at {config.schedule_time}")
    
    # Clear any existing jobs
    schedule.clear()
    
    # Configure the weekly job
    if config.schedule_day == 'monday':
        schedule.every().monday.at(config.schedule_time).do(run_weekly_processing)
    elif config.schedule_day == 'tuesday':
        schedule.every().tuesday.at(config.schedule_time).do(run_weekly_processing)
    elif config.schedule_day == 'wednesday':
        schedule.every().wednesday.at(config.schedule_time).do(run_weekly_processing)
    elif config.schedule_day == 'thursday':
        schedule.every().thursday.at(config.schedule_time).do(run_weekly_processing)
    elif config.schedule_day == 'friday':
        schedule.every().friday.at(config.schedule_time).do(run_weekly_processing)
    elif config.schedule_day == 'saturday':
        schedule.every().saturday.at(config.schedule_time).do(run_weekly_processing)
    elif config.schedule_day == 'sunday':
        schedule.every().sunday.at(config.schedule_time).do(run_weekly_processing)
    else:
        logger.error(f"Invalid schedule day: {config.schedule_day}")
        raise ValueError(f"Invalid schedule day: {config.schedule_day}")
    
    # Log next run time
    next_run = schedule.next_run()
    if next_run:
        logger.info(f"Next scheduled run: {next_run.isoformat()}")
    
    return len(schedule.jobs)

def run_scheduler():
    """Main scheduler loop"""
    logger.info("=== LCF Civic Summaries Scheduler Starting ===")
    logger.info(f"Environment: {config.environment}")
    logger.info(f"Timezone: {config.timezone}")
    
    # Configure the schedule
    job_count = configure_schedule()
    logger.info(f"Configured {job_count} scheduled job(s)")
    
    # Send startup notification
    send_alert("LCF Civic Summaries scheduler started successfully", "info")
    
    # Main scheduler loop
    logger.info("Scheduler is running. Press Ctrl+C to stop.")
    
    try:
        while True:
            # Check for pending jobs
            schedule.run_pending()
            
            # Sleep for 60 seconds before checking again
            time.sleep(60)
            
            # Log heartbeat every hour
            current_time = datetime.utcnow()
            if current_time.minute == 0:
                next_run = schedule.next_run()
                if next_run:
                    time_until_next = next_run - current_time
                    logger.info(f"Scheduler heartbeat - Next run in {time_until_next}")
                
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
        send_alert("LCF Civic Summaries scheduler stopped", "warning")
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        send_alert(f"Scheduler crashed: {str(e)}", "error")
        raise

def test_configuration():
    """Test scheduler configuration and dependencies"""
    logger.info("=== Testing Scheduler Configuration ===")
    
    # Test environment variables
    missing_vars = []
    if not config.openai_api_key:
        missing_vars.append('OPENAI_API_KEY')
    if not config.smtp_username:
        missing_vars.append('SMTP_USERNAME')
    if not config.smtp_password:
        missing_vars.append('SMTP_PASSWORD')
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
    else:
        logger.info("All required environment variables are configured")
    
    # Test data directory
    try:
        test_file = os.path.join(config.data_dir, 'scheduler_test.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        logger.info(f"Data directory is writable: {config.data_dir}")
    except Exception as e:
        logger.error(f"Data directory is not writable: {str(e)}")
    
    # Test schedule configuration
    try:
        configure_schedule()
        logger.info("Schedule configuration is valid")
    except Exception as e:
        logger.error(f"Schedule configuration error: {str(e)}")
    
    logger.info("=== Configuration Test Complete ===")

if __name__ == '__main__':
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_configuration()
        
        # Run a test processing cycle if requested
        if len(sys.argv) > 2 and sys.argv[2] == '--run':
            logger.info("Running test processing cycle...")
            run_weekly_processing()
    else:
        # Run the main scheduler
        run_scheduler()

