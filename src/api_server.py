#!/usr/bin/env python3
"""
LCF Civic Summaries API Server
Railway-optimized version with environment variable configuration
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all origins (required for Lovable integration)
CORS(app, origins=['*'])

# Configuration from environment variables
class Config:
    def __init__(self):
        self.data_dir = os.getenv('DATA_DIR', 'data')
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.port = int(os.getenv('PORT', 5000))
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        logger.info(f"API Server configured - Environment: {self.environment}, Port: {self.port}")

config = Config()

def load_json_file(filename, default=None):
    """Load JSON file with error handling"""
    file_path = os.path.join(config.data_dir, filename)
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

def save_json_file(filename, data):
    """Save JSON file with error handling"""
    file_path = os.path.join(config.data_dir, filename)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Saved data to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving {filename}: {str(e)}")
        return False

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': config.environment,
        'version': '1.0.0'
    })

@app.route('/api/health/detailed')
def detailed_health_check():
    """Detailed health check with system status"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': config.environment,
        'checks': {}
    }
    
    # Check data directory access
    try:
        test_file = os.path.join(config.data_dir, 'health_check.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        health_status['checks']['storage'] = 'healthy'
    except Exception as e:
        health_status['checks']['storage'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Check environment variables
    required_vars = ['OPENAI_API_KEY', 'SMTP_USERNAME', 'SMTP_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        health_status['checks']['environment'] = f'missing variables: {", ".join(missing_vars)}'
        health_status['status'] = 'degraded'
    else:
        health_status['checks']['environment'] = 'healthy'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code

@app.route('/api/summaries')
def get_summaries():
    """Get current meeting summaries"""
    try:
        summaries = load_json_file('website_data.json', {})
        
        # Add metadata
        response_data = {
            'summaries': summaries.get('summaries', []),
            'statistics': summaries.get('statistics', {}),
            'last_updated': summaries.get('last_updated'),
            'total_count': len(summaries.get('summaries', []))
        }
        
        logger.info(f"Served {response_data['total_count']} current summaries")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error serving summaries: {str(e)}")
        return jsonify({'error': 'Failed to load summaries'}), 500

@app.route('/api/archive')
def get_archive():
    """Get historical archive data"""
    try:
        archive_data = load_json_file('combined_website_data.json', {})
        
        # Structure archive data by month and government body
        archive_summaries = archive_data.get('archive_summaries', [])
        
        # Group by month
        monthly_data = {}
        for summary in archive_summaries:
            month_key = summary.get('month', 'Unknown')
            if month_key not in monthly_data:
                monthly_data[month_key] = []
            monthly_data[month_key].append(summary)
        
        response_data = {
            'archive': monthly_data,
            'statistics': {
                'total_documents': len(archive_summaries),
                'months_covered': len(monthly_data),
                'government_bodies': len(set(s.get('government_body', '') for s in archive_summaries)),
                'ai_summaries': len([s for s in archive_summaries if s.get('ai_generated', False)])
            },
            'last_updated': archive_data.get('last_updated')
        }
        
        logger.info(f"Served archive data: {response_data['statistics']['total_documents']} documents")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error serving archive: {str(e)}")
        return jsonify({'error': 'Failed to load archive data'}), 500

@app.route('/api/government-bodies')
def get_government_bodies():
    """Get list of government bodies being tracked"""
    try:
        summaries = load_json_file('website_data.json', {})
        archive_data = load_json_file('combined_website_data.json', {})
        
        # Extract unique government bodies
        current_bodies = set()
        for summary in summaries.get('summaries', []):
            current_bodies.add(summary.get('government_body', ''))
        
        archive_bodies = set()
        for summary in archive_data.get('archive_summaries', []):
            archive_bodies.add(summary.get('government_body', ''))
        
        all_bodies = sorted(list(current_bodies.union(archive_bodies)))
        
        return jsonify({
            'government_bodies': all_bodies,
            'current_count': len(current_bodies),
            'archive_count': len(archive_bodies),
            'total_count': len(all_bodies)
        })
        
    except Exception as e:
        logger.error(f"Error serving government bodies: {str(e)}")
        return jsonify({'error': 'Failed to load government bodies'}), 500

@app.route('/api/search')
def search_summaries():
    """Search through summaries and archive"""
    query = request.args.get('q', '').lower()
    government_body = request.args.get('body', '')
    
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    try:
        # Load current summaries
        current_data = load_json_file('website_data.json', {})
        archive_data = load_json_file('combined_website_data.json', {})
        
        results = []
        
        # Search current summaries
        for summary in current_data.get('summaries', []):
            if government_body and summary.get('government_body', '') != government_body:
                continue
                
            summary_text = summary.get('summary', '').lower()
            title = summary.get('title', '').lower()
            
            if query in summary_text or query in title:
                results.append({
                    **summary,
                    'source': 'current'
                })
        
        # Search archive
        for summary in archive_data.get('archive_summaries', []):
            if government_body and summary.get('government_body', '') != government_body:
                continue
                
            summary_text = summary.get('summary', '').lower()
            title = summary.get('title', '').lower()
            
            if query in summary_text or query in title:
                results.append({
                    **summary,
                    'source': 'archive'
                })
        
        logger.info(f"Search for '{query}' returned {len(results)} results")
        
        return jsonify({
            'query': query,
            'government_body': government_body,
            'results': results,
            'total_count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

@app.route('/api/trigger-processing', methods=['POST'])
def trigger_processing():
    """Manually trigger processing (for testing)"""
    if config.environment != 'production':
        try:
            # Import and run processing functions
            import threading
            
            def run_processing():
                try:
                    logger.info("Manual processing triggered")
                    # This would call your processing functions
                    # For now, just log the trigger
                    logger.info("Processing completed (test mode)")
                except Exception as e:
                    logger.error(f"Processing failed: {str(e)}")
            
            # Run in background thread
            thread = threading.Thread(target=run_processing)
            thread.start()
            
            return jsonify({
                'status': 'success',
                'message': 'Processing started in background'
            })
            
        except Exception as e:
            logger.error(f"Failed to trigger processing: {str(e)}")
            return jsonify({'error': 'Failed to start processing'}), 500
    else:
        return jsonify({'error': 'Manual triggering disabled in production'}), 403

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

# Add this code to your src/api_server.py file in Railway
# Insert this code before the "if __name__ == '__main__':" line

@app.route('/api/test-workflow', methods=['POST', 'GET'])
def test_workflow():
    """Run comprehensive workflow tests via API endpoint"""
    
    # Only allow testing in non-production environments or when explicitly enabled
    if config.environment == 'production' and not os.getenv('ENABLE_TESTING', 'false').lower() == 'true':
        return jsonify({'error': 'Testing disabled in production. Set ENABLE_TESTING=true to enable.'}), 403
    
    try:
        test_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'environment': config.environment,
            'test_summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            },
            'tests': {}
        }
        
        logger.info("Starting comprehensive workflow tests via API")
        
        # Test 1: Check Python Dependencies
        logger.info("Test 1: Checking Python dependencies")
        try:
            import requests
            import beautifulsoup4
            import openai
            import schedule
            import flask
            from flask_cors import CORS
            
            # Check versions
            import pkg_resources
            packages = ['requests', 'beautifulsoup4', 'openai', 'schedule', 'flask', 'flask-cors']
            versions = {}
            
            for package in packages:
                try:
                    version = pkg_resources.get_distribution(package).version
                    versions[package] = version
                except:
                    versions[package] = 'unknown'
            
            test_results['tests']['dependencies'] = {
                'status': 'PASS',
                'message': 'All required packages available',
                'versions': versions
            }
            test_results['test_summary']['passed'] += 1
            
        except ImportError as e:
            test_results['tests']['dependencies'] = {
                'status': 'FAIL',
                'message': f'Missing dependency: {str(e)}',
                'error': str(e)
            }
            test_results['test_summary']['failed'] += 1
        
        test_results['test_summary']['total_tests'] += 1
        
        # Test 2: Check Data Directory Access
        logger.info("Test 2: Checking data directory access")
        try:
            data_dir = config.data_dir
            
            # Test directory creation
            os.makedirs(data_dir, exist_ok=True)
            
            # Test file write/read/delete
            test_file = os.path.join(data_dir, 'workflow_test.tmp')
            test_content = f"Test file created at {datetime.utcnow().isoformat()}"
            
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            with open(test_file, 'r', encoding='utf-8') as f:
                read_content = f.read()
            
            os.remove(test_file)
            
            if read_content == test_content:
                test_results['tests']['data_directory'] = {
                    'status': 'PASS',
                    'message': f'Data directory accessible at {data_dir}',
                    'path': data_dir
                }
                test_results['test_summary']['passed'] += 1
            else:
                test_results['tests']['data_directory'] = {
                    'status': 'FAIL',
                    'message': 'File read/write test failed',
                    'path': data_dir
                }
                test_results['test_summary']['failed'] += 1
                
        except Exception as e:
            test_results['tests']['data_directory'] = {
                'status': 'FAIL',
                'message': f'Data directory access failed: {str(e)}',
                'error': str(e)
            }
            test_results['test_summary']['failed'] += 1
        
        test_results['test_summary']['total_tests'] += 1
        
        # Test 3: Check Environment Variables
        logger.info("Test 3: Checking environment variables")
        required_vars = {
            'OPENAI_API_KEY': 'OpenAI API access',
            'SMTP_USERNAME': 'Email notifications',
            'SMTP_PASSWORD': 'Email authentication',
            'EMAIL_FROM': 'Email sender',
            'EMAIL_TO': 'Email recipient'
        }
        
        optional_vars = {
            'OPENAI_MODEL': 'AI model selection',
            'MAX_TOKENS': 'AI response length',
            'SCHEDULE_TIME': 'Job scheduling',
            'SCHEDULE_DAY': 'Job scheduling'
        }
        
        env_status = {
            'required': {},
            'optional': {},
            'missing_required': [],
            'missing_optional': []
        }
        
        for var, description in required_vars.items():
            value = os.getenv(var)
            if value:
                env_status['required'][var] = 'configured'
            else:
                env_status['required'][var] = 'missing'
                env_status['missing_required'].append(var)
        
        for var, description in optional_vars.items():
            value = os.getenv(var)
            if value:
                env_status['optional'][var] = value
            else:
                env_status['optional'][var] = 'not set'
                env_status['missing_optional'].append(var)
        
        if not env_status['missing_required']:
            test_results['tests']['environment_variables'] = {
                'status': 'PASS',
                'message': 'All required environment variables configured',
                'details': env_status
            }
            test_results['test_summary']['passed'] += 1
        else:
            test_results['tests']['environment_variables'] = {
                'status': 'FAIL',
                'message': f'Missing required variables: {env_status["missing_required"]}',
                'details': env_status
            }
            test_results['test_summary']['failed'] += 1
        
        if env_status['missing_optional']:
            test_results['test_summary']['warnings'] += 1
        
        test_results['test_summary']['total_tests'] += 1
        
        # Test 4: Check OpenAI API Connection
        logger.info("Test 4: Checking OpenAI API connection")
        if os.getenv('OPENAI_API_KEY'):
            try:
                import openai
                
                # Try to initialize OpenAI client
                try:
                    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                    # Test with a minimal API call
                    response = client.chat.completions.create(
                        model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                        messages=[{"role": "user", "content": "Test"}],
                        max_tokens=5
                    )
                    
                    test_results['tests']['openai_api'] = {
                        'status': 'PASS',
                        'message': 'OpenAI API connection successful',
                        'model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
                    }
                    test_results['test_summary']['passed'] += 1
                    
                except Exception as api_error:
                    test_results['tests']['openai_api'] = {
                        'status': 'FAIL',
                        'message': f'OpenAI API call failed: {str(api_error)}',
                        'error': str(api_error)
                    }
                    test_results['test_summary']['failed'] += 1
                    
            except ImportError:
                test_results['tests']['openai_api'] = {
                    'status': 'FAIL',
                    'message': 'OpenAI library not available',
                    'error': 'Import error'
                }
                test_results['test_summary']['failed'] += 1
        else:
            test_results['tests']['openai_api'] = {
                'status': 'SKIP',
                'message': 'OpenAI API key not configured',
                'note': 'Set OPENAI_API_KEY to test AI functionality'
            }
            test_results['test_summary']['warnings'] += 1
        
        test_results['test_summary']['total_tests'] += 1
        
        # Test 5: Check API Endpoints
        logger.info("Test 5: Checking internal API endpoints")
        try:
            # Test health endpoint internally
            with app.test_client() as client:
                health_response = client.get('/api/health')
                summaries_response = client.get('/api/summaries')
                bodies_response = client.get('/api/government-bodies')
                
                endpoint_tests = {
                    '/api/health': health_response.status_code == 200,
                    '/api/summaries': summaries_response.status_code == 200,
                    '/api/government-bodies': bodies_response.status_code == 200
                }
                
                failed_endpoints = [ep for ep, success in endpoint_tests.items() if not success]
                
                if not failed_endpoints:
                    test_results['tests']['api_endpoints'] = {
                        'status': 'PASS',
                        'message': 'All API endpoints responding correctly',
                        'endpoints_tested': list(endpoint_tests.keys())
                    }
                    test_results['test_summary']['passed'] += 1
                else:
                    test_results['tests']['api_endpoints'] = {
                        'status': 'FAIL',
                        'message': f'Failed endpoints: {failed_endpoints}',
                        'details': endpoint_tests
                    }
                    test_results['test_summary']['failed'] += 1
                    
        except Exception as e:
            test_results['tests']['api_endpoints'] = {
                'status': 'FAIL',
                'message': f'API endpoint testing failed: {str(e)}',
                'error': str(e)
            }
            test_results['test_summary']['failed'] += 1
        
        test_results['test_summary']['total_tests'] += 1
        
        # Test 6: Check Email Configuration
        logger.info("Test 6: Checking email configuration")
        email_vars = ['SMTP_USERNAME', 'SMTP_PASSWORD', 'EMAIL_FROM', 'EMAIL_TO']
        email_configured = all(os.getenv(var) for var in email_vars)
        
        if email_configured:
            try:
                import smtplib
                from email.mime.text import MIMEText
                
                # Test SMTP connection (don't send actual email)
                smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
                smtp_port = int(os.getenv('SMTP_PORT', '587'))
                
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
                server.quit()
                
                test_results['tests']['email_configuration'] = {
                    'status': 'PASS',
                    'message': 'Email configuration valid and SMTP connection successful',
                    'smtp_server': smtp_server,
                    'smtp_port': smtp_port
                }
                test_results['test_summary']['passed'] += 1
                
            except Exception as e:
                test_results['tests']['email_configuration'] = {
                    'status': 'FAIL',
                    'message': f'Email configuration test failed: {str(e)}',
                    'error': str(e)
                }
                test_results['test_summary']['failed'] += 1
        else:
            missing_email_vars = [var for var in email_vars if not os.getenv(var)]
            test_results['tests']['email_configuration'] = {
                'status': 'SKIP',
                'message': f'Email not configured. Missing: {missing_email_vars}',
                'note': 'Configure email variables to enable notifications'
            }
            test_results['test_summary']['warnings'] += 1
        
        test_results['test_summary']['total_tests'] += 1
        
        # Test 7: Test Document Processing Functions
        logger.info("Test 7: Testing document processing functions")
        try:
            # Test if we can import the processing modules
            from fetch_all_meetings import RailwayMeetingsFetcher
            from summarize_all_meetings import RailwaySummarizer
            from update_website_data import RailwayWebsiteUpdater
            
            # Test basic initialization
            fetcher = RailwayMeetingsFetcher()
            summarizer = RailwaySummarizer()
            updater = RailwayWebsiteUpdater()
            
            test_results['tests']['processing_modules'] = {
                'status': 'PASS',
                'message': 'All processing modules imported and initialized successfully',
                'modules': ['fetch_all_meetings', 'summarize_all_meetings', 'update_website_data']
            }
            test_results['test_summary']['passed'] += 1
            
        except ImportError as e:
            test_results['tests']['processing_modules'] = {
                'status': 'FAIL',
                'message': f'Failed to import processing modules: {str(e)}',
                'error': str(e)
            }
            test_results['test_summary']['failed'] += 1
        except Exception as e:
            test_results['tests']['processing_modules'] = {
                'status': 'FAIL',
                'message': f'Failed to initialize processing modules: {str(e)}',
                'error': str(e)
            }
            test_results['test_summary']['failed'] += 1
        
        test_results['test_summary']['total_tests'] += 1
        
        # Calculate overall status
        if test_results['test_summary']['failed'] == 0:
            if test_results['test_summary']['warnings'] == 0:
                overall_status = 'ALL_PASS'
                status_message = 'All tests passed successfully!'
            else:
                overall_status = 'PASS_WITH_WARNINGS'
                status_message = f'Tests passed with {test_results["test_summary"]["warnings"]} warnings'
        else:
            overall_status = 'SOME_FAILURES'
            status_message = f'{test_results["test_summary"]["failed"]} tests failed'
        
        test_results['overall_status'] = overall_status
        test_results['status_message'] = status_message
        
        logger.info(f"Workflow tests completed: {status_message}")
        
        # Return appropriate HTTP status
        if overall_status == 'ALL_PASS':
            return jsonify(test_results), 200
        elif overall_status == 'PASS_WITH_WARNINGS':
            return jsonify(test_results), 200
        else:
            return jsonify(test_results), 206  # Partial Content
            
    except Exception as e:
        logger.error(f"Test workflow execution failed: {str(e)}")
        return jsonify({
            'error': f'Test execution failed: {str(e)}',
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'ERROR'
        }), 500

@app.route('/api/test-simple', methods=['GET'])
def test_simple():
    """Run a simple quick test"""
    try:
        simple_tests = {
            'timestamp': datetime.utcnow().isoformat(),
            'api_server': 'running',
            'environment': config.environment,
            'data_dir': config.data_dir,
            'data_dir_exists': os.path.exists(config.data_dir),
            'openai_configured': bool(os.getenv('OPENAI_API_KEY')),
            'email_configured': bool(os.getenv('SMTP_USERNAME') and os.getenv('SMTP_PASSWORD'))
        }
        
        return jsonify(simple_tests), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

if __name__ == '__main__':
    logger.info(f"Starting LCF Civic Summaries API Server on port {config.port}")
    logger.info(f"Environment: {config.environment}")
    logger.info(f"Data directory: {config.data_dir}")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',  # Required for Railway deployment
        port=config.port,
        debug=config.debug
    )

