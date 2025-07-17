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

