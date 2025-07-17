#!/usr/bin/env python3
"""
La Canada Flintridge Government Meetings Tracker - Test Workflow
Tests the complete workflow from document fetching to email reporting.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Import our modules
import fetch_all_meetings
import summarize_all_meetings
import send_consolidated_email

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lcf_test_workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WorkflowTester:
    """Tests the complete workflow of the LCF government tracker."""
    
    def __init__(self, config_path="config.json"):
        """Initialize the workflow tester."""
        self.config_path = config_path
        self.test_results = {
            "fetch": False,
            "summarize": False,
            "email": False,
            "overall": False
        }
    
    def test_document_fetching(self):
        """Test the document fetching functionality."""
        logger.info("Testing document fetching...")
        
        try:
            # Create fetcher instance
            fetcher = fetch_all_meetings.MeetingDocumentFetcher(self.config_path)
            
            # Test fetching documents
            documents = fetcher.fetch_all_documents()
            
            if documents:
                # Check if we got data for at least one government body
                has_documents = False
                for body_name, body_data in documents.items():
                    if body_data.get("agendas") or body_data.get("minutes"):
                        has_documents = True
                        break
                
                if has_documents:
                    logger.info("✓ Document fetching test passed")
                    self.test_results["fetch"] = True
                    return documents
                else:
                    logger.warning("⚠ Document fetching returned empty results")
                    return documents  # Still return for testing other components
            else:
                logger.error("✗ Document fetching test failed - no data returned")
                return None
                
        except Exception as e:
            logger.error(f"✗ Document fetching test failed with error: {e}")
            return None
    
    def test_summarization(self, documents_data):
        """Test the document summarization functionality."""
        logger.info("Testing document summarization...")
        
        if not documents_data:
            logger.error("✗ Cannot test summarization - no documents data provided")
            return None
        
        try:
            # Create summarizer instance
            summarizer = summarize_all_meetings.MeetingSummarizer(self.config_path)
            
            # Test summarization
            summaries = summarizer.summarize_documents(documents_data)
            
            if summaries:
                # Check if we got summaries for at least one document
                has_summaries = False
                for body_name, body_data in summaries.items():
                    if body_data.get("agendas") or body_data.get("minutes"):
                        has_summaries = True
                        break
                
                if has_summaries:
                    logger.info("✓ Document summarization test passed")
                    self.test_results["summarize"] = True
                    return summaries
                else:
                    logger.warning("⚠ Document summarization returned empty results")
                    return summaries
            else:
                logger.error("✗ Document summarization test failed - no summaries returned")
                return None
                
        except Exception as e:
            logger.error(f"✗ Document summarization test failed with error: {e}")
            return None
    
    def test_email_reporting(self, summaries_data):
        """Test the email reporting functionality."""
        logger.info("Testing email reporting...")
        
        if not summaries_data:
            logger.error("✗ Cannot test email reporting - no summaries data provided")
            return False
        
        try:
            # Create reporter instance
            reporter = send_consolidated_email.EmailReporter(self.config_path)
            
            # Test report generation (but don't actually send email)
            # Temporarily disable email sending for testing
            original_send_email = reporter.config.get("send_email", False)
            reporter.config["send_email"] = False
            
            # Test report generation
            success = reporter.generate_and_send_report(summaries_data)
            
            # Restore original email setting
            reporter.config["send_email"] = original_send_email
            
            if success:
                logger.info("✓ Email reporting test passed")
                self.test_results["email"] = True
                return True
            else:
                logger.error("✗ Email reporting test failed")
                return False
                
        except Exception as e:
            logger.error(f"✗ Email reporting test failed with error: {e}")
            return False
    
    def test_configuration(self):
        """Test configuration file loading."""
        logger.info("Testing configuration...")
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                logger.info("✓ Configuration file loaded successfully")
                
                # Check for required fields
                required_fields = ["enabled_bodies", "openai_api_key", "email_from", "email_to"]
                missing_fields = []
                
                for field in required_fields:
                    if field not in config or not config[field]:
                        missing_fields.append(field)
                
                if missing_fields:
                    logger.warning(f"⚠ Configuration missing or empty fields: {', '.join(missing_fields)}")
                else:
                    logger.info("✓ All required configuration fields present")
                
                return True
            else:
                logger.warning(f"⚠ Configuration file {self.config_path} not found - using defaults")
                return True
                
        except json.JSONDecodeError:
            logger.error(f"✗ Configuration file {self.config_path} contains invalid JSON")
            return False
        except Exception as e:
            logger.error(f"✗ Configuration test failed with error: {e}")
            return False
    
    def test_dependencies(self):
        """Test that all required dependencies are available."""
        logger.info("Testing dependencies...")
        
        required_modules = [
            "requests",
            "beautifulsoup4", 
            "PyPDF2",
            "openai",
            "schedule"
        ]
        
        missing_modules = []
        
        for module in required_modules:
            try:
                if module == "beautifulsoup4":
                    import bs4
                    logger.info(f"✓ {module} is available")
                elif module == "openai":
                    import openai
                    logger.info(f"✓ {module} is available (API connectivity will be tested separately)")
                else:
                    __import__(module)
                    logger.info(f"✓ {module} is available")
            except ImportError:
                logger.error(f"✗ {module} is not available")
                missing_modules.append(module)
        
        if missing_modules:
            logger.error(f"✗ Missing required modules: {', '.join(missing_modules)}")
            return False
        else:
            logger.info("✓ All required dependencies are available")
            return True
    
    def run_complete_test(self):
        """Run the complete workflow test."""
        logger.info("="*60)
        logger.info("STARTING LA CAÑADA FLINTRIDGE GOVERNMENT TRACKER TEST")
        logger.info("="*60)
        
        start_time = datetime.now()
        
        # Test 1: Dependencies
        logger.info("\n1. Testing Dependencies...")
        deps_ok = self.test_dependencies()
        
        # Test 2: Configuration
        logger.info("\n2. Testing Configuration...")
        config_ok = self.test_configuration()
        
        # Test 3: Document Fetching
        logger.info("\n3. Testing Document Fetching...")
        documents = self.test_document_fetching()
        
        # Test 4: Document Summarization
        logger.info("\n4. Testing Document Summarization...")
        summaries = self.test_summarization(documents)
        
        # Test 5: Email Reporting
        logger.info("\n5. Testing Email Reporting...")
        email_ok = self.test_email_reporting(summaries)
        
        # Calculate overall result
        self.test_results["overall"] = all([
            deps_ok,
            config_ok,
            self.test_results["fetch"],
            self.test_results["summarize"],
            self.test_results["email"]
        ])
        
        # Print results
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("\n" + "="*60)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("="*60)
        logger.info(f"Dependencies:     {'✓ PASS' if deps_ok else '✗ FAIL'}")
        logger.info(f"Configuration:    {'✓ PASS' if config_ok else '✗ FAIL'}")
        logger.info(f"Document Fetch:   {'✓ PASS' if self.test_results['fetch'] else '✗ FAIL'}")
        logger.info(f"Summarization:    {'✓ PASS' if self.test_results['summarize'] else '✗ FAIL'}")
        logger.info(f"Email Reporting:  {'✓ PASS' if self.test_results['email'] else '✗ FAIL'}")
        logger.info("-" * 60)
        logger.info(f"Overall Result:   {'✓ PASS' if self.test_results['overall'] else '✗ FAIL'}")
        logger.info(f"Test Duration:    {duration.total_seconds():.2f} seconds")
        logger.info("="*60)
        
        if self.test_results["overall"]:
            logger.info("🎉 All tests passed! The LCF Government Tracker is ready to use.")
        else:
            logger.info("⚠️  Some tests failed. Please check the logs and fix any issues before using the tracker.")
        
        return self.test_results

def main():
    """Main entry point for the test script."""
    try:
        tester = WorkflowTester()
        results = tester.run_complete_test()
        
        # Return appropriate exit code
        if results["overall"]:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except Exception as e:
        logger.error(f"Test workflow failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

