#!/usr/bin/env python3
"""
LCF Civic Summaries API Server
Clean REST API for external frontend integration (Lovable, etc.)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class LCFAPIServer:
    def __init__(self):
        self.data_dir = os.path.dirname(os.path.abspath(__file__))
        
    def load_json_file(self, filename):
        """Load JSON data from file with error handling"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"File not found: {filepath}")
                return None
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return None
    
    def get_current_summaries(self):
        """Get current meeting summaries"""
        data = self.load_json_file('document_summaries.json')
        if not data:
            return self.create_mock_current_data()
        
        # Transform data for frontend consumption
        transformed = {}
        for body_name, body_data in data.items():
            transformed[body_name] = {
                'agendas': [],
                'minutes': []
            }
            
            # Process agendas
            if 'agendas' in body_data:
                for agenda in body_data['agendas']:
                    transformed[body_name]['agendas'].append({
                        'id': f"{body_name}_agenda_{agenda.get('date', 'unknown')}",
                        'title': agenda.get('title', f"{body_name} Agenda"),
                        'date': agenda.get('date', datetime.now().isoformat()),
                        'summary': agenda.get('summary', 'No summary available'),
                        'url': agenda.get('url', '#'),
                        'type': 'agenda',
                        'ai_generated': agenda.get('ai_generated', False),
                        'body': body_name
                    })
            
            # Process minutes
            if 'minutes' in body_data:
                for minute in body_data['minutes']:
                    transformed[body_name]['minutes'].append({
                        'id': f"{body_name}_minutes_{minute.get('date', 'unknown')}",
                        'title': minute.get('title', f"{body_name} Minutes"),
                        'date': minute.get('date', datetime.now().isoformat()),
                        'summary': minute.get('summary', 'No summary available'),
                        'url': minute.get('url', '#'),
                        'type': 'minutes',
                        'ai_generated': minute.get('ai_generated', False),
                        'body': body_name
                    })
        
        return transformed
    
    def get_historical_archive(self):
        """Get historical archive data"""
        # Try to load from historical summaries
        historical_data = self.load_json_file('historical_summaries_2025/historical_summaries_2025.json')
        if historical_data:
            return self.transform_historical_data(historical_data)
        
        # Try combined website data
        combined_data = self.load_json_file('combined_website_data.json')
        if combined_data and 'archive' in combined_data:
            return combined_data['archive']
        
        # Fallback to mock data
        return self.create_mock_archive_data()
    
    def transform_historical_data(self, data):
        """Transform historical data for frontend consumption"""
        transformed = {}
        
        for body_name, body_data in data.items():
            transformed[body_name] = {
                'agendas': [],
                'minutes': []
            }
            
            # Process historical documents
            if isinstance(body_data, dict):
                for doc_type, documents in body_data.items():
                    if isinstance(documents, list):
                        for doc in documents:
                            doc_item = {
                                'id': f"{body_name}_{doc_type}_{doc.get('date', 'unknown')}",
                                'title': doc.get('title', f"{body_name} {doc_type.title()}"),
                                'date': doc.get('date', datetime.now().isoformat()),
                                'summary': doc.get('summary', 'No summary available'),
                                'url': doc.get('url', '#'),
                                'type': doc_type.rstrip('s'),  # Remove plural
                                'ai_generated': doc.get('ai_generated', True),
                                'historical': True,
                                'body': body_name,
                                'month': doc.get('month', 'June 2025')
                            }
                            
                            if doc_type == 'agendas':
                                transformed[body_name]['agendas'].append(doc_item)
                            elif doc_type == 'minutes':
                                transformed[body_name]['minutes'].append(doc_item)
        
        return transformed
    
    def create_mock_current_data(self):
        """Create mock current data for testing"""
        return {
            "City Council": {
                "agendas": [
                    {
                        "id": "city_council_agenda_2025_07_16",
                        "title": "City Council Agenda - July 16, 2025",
                        "date": "2025-07-16T19:00:00",
                        "summary": "Regular meeting agenda including budget discussions, infrastructure updates, and community development projects.",
                        "url": "https://lcf.ca.gov/city-clerk/agenda-minutes/",
                        "type": "agenda",
                        "ai_generated": True,
                        "body": "City Council"
                    }
                ],
                "minutes": [
                    {
                        "id": "city_council_minutes_2025_07_02",
                        "title": "City Council Minutes - July 2, 2025",
                        "date": "2025-07-02T19:00:00",
                        "summary": "Council approved the annual budget with amendments for increased public safety funding and park improvements.",
                        "url": "https://lcf.ca.gov/city-clerk/agenda-minutes/",
                        "type": "minutes",
                        "ai_generated": True,
                        "body": "City Council"
                    }
                ]
            },
            "Planning Commission": {
                "agendas": [
                    {
                        "id": "planning_commission_agenda_2025_07_15",
                        "title": "Planning Commission Agenda - July 15, 2025",
                        "date": "2025-07-15T18:00:00",
                        "summary": "Review of proposed residential development and updates to zoning ordinances.",
                        "url": "https://lcf.ca.gov/city-clerk/agenda-minutes/",
                        "type": "agenda",
                        "ai_generated": True,
                        "body": "Planning Commission"
                    }
                ],
                "minutes": []
            }
        }
    
    def create_mock_archive_data(self):
        """Create mock archive data for testing"""
        return {
            "City Council": {
                "agendas": [
                    {
                        "id": "city_council_agenda_2025_06_21",
                        "title": "City Council Agenda - June 21, 2025",
                        "date": "2025-06-21T19:00:00",
                        "summary": "Budget workshop session focusing on the FY 2025-26 proposed budget. Discussion of capital improvement projects including street resurfacing, park upgrades, and technology infrastructure improvements.",
                        "url": "https://lcf.ca.gov/city-clerk/agenda-minutes/",
                        "type": "agenda",
                        "ai_generated": True,
                        "historical": True,
                        "body": "City Council",
                        "month": "June 2025"
                    }
                ],
                "minutes": [
                    {
                        "id": "city_council_minutes_2025_06_14",
                        "title": "City Council Minutes - June 14, 2025",
                        "date": "2025-06-14T19:00:00",
                        "summary": "Council unanimously approved the $15.2M annual budget with amendments to increase funding for road maintenance and public safety equipment.",
                        "url": "https://lcf.ca.gov/city-clerk/agenda-minutes/",
                        "type": "minutes",
                        "ai_generated": True,
                        "historical": True,
                        "body": "City Council",
                        "month": "June 2025"
                    }
                ]
            },
            "Planning Commission": {
                "agendas": [
                    {
                        "id": "planning_commission_agenda_2025_06_16",
                        "title": "Planning Commission Agenda - June 16, 2025",
                        "date": "2025-06-16T18:00:00",
                        "summary": "Review of the proposed mixed-use development at 1500 Foothill Boulevard and consideration of amendments to the hillside development ordinance.",
                        "url": "https://lcf.ca.gov/city-clerk/agenda-minutes/",
                        "type": "agenda",
                        "ai_generated": True,
                        "historical": True,
                        "body": "Planning Commission",
                        "month": "June 2025"
                    }
                ],
                "minutes": [
                    {
                        "id": "planning_commission_minutes_2025_06_02",
                        "title": "Planning Commission Minutes - June 2, 2025",
                        "date": "2025-06-02T18:00:00",
                        "summary": "Commission approved the conditional use permit for the expanded medical facility with conditions for enhanced landscaping and traffic management.",
                        "url": "https://lcf.ca.gov/city-clerk/agenda-minutes/",
                        "type": "minutes",
                        "ai_generated": True,
                        "historical": True,
                        "body": "Planning Commission",
                        "month": "June 2025"
                    }
                ]
            }
        }
    
    def get_stats(self, data):
        """Calculate statistics for the data"""
        stats = {
            'total_documents': 0,
            'total_bodies': len(data),
            'total_agendas': 0,
            'total_minutes': 0,
            'ai_summaries': 0,
            'months': set()
        }
        
        for body_data in data.values():
            if 'agendas' in body_data:
                stats['total_agendas'] += len(body_data['agendas'])
                stats['total_documents'] += len(body_data['agendas'])
                stats['ai_summaries'] += sum(1 for doc in body_data['agendas'] if doc.get('ai_generated'))
                for doc in body_data['agendas']:
                    if doc.get('month'):
                        stats['months'].add(doc['month'])
            
            if 'minutes' in body_data:
                stats['total_minutes'] += len(body_data['minutes'])
                stats['total_documents'] += len(body_data['minutes'])
                stats['ai_summaries'] += sum(1 for doc in body_data['minutes'] if doc.get('ai_generated'))
                for doc in body_data['minutes']:
                    if doc.get('month'):
                        stats['months'].add(doc['month'])
        
        stats['total_months'] = len(stats['months'])
        stats['months'] = list(stats['months'])
        
        return stats

# Initialize API server
api_server = LCFAPIServer()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'LCF Civic Summaries API'
    })

@app.route('/api/current', methods=['GET'])
def get_current_summaries():
    """Get current meeting summaries"""
    try:
        data = api_server.get_current_summaries()
        stats = api_server.get_stats(data)
        
        return jsonify({
            'success': True,
            'data': data,
            'stats': stats,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in get_current_summaries: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/archive', methods=['GET'])
def get_historical_archive():
    """Get historical archive data"""
    try:
        data = api_server.get_historical_archive()
        stats = api_server.get_stats(data)
        
        return jsonify({
            'success': True,
            'data': data,
            'stats': stats,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in get_historical_archive: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/all', methods=['GET'])
def get_all_data():
    """Get both current and archive data"""
    try:
        current_data = api_server.get_current_summaries()
        archive_data = api_server.get_historical_archive()
        
        current_stats = api_server.get_stats(current_data)
        archive_stats = api_server.get_stats(archive_data)
        
        return jsonify({
            'success': True,
            'current': {
                'data': current_data,
                'stats': current_stats
            },
            'archive': {
                'data': archive_data,
                'stats': archive_stats
            },
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in get_all_data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bodies', methods=['GET'])
def get_government_bodies():
    """Get list of all government bodies"""
    try:
        current_data = api_server.get_current_summaries()
        archive_data = api_server.get_historical_archive()
        
        bodies = set()
        bodies.update(current_data.keys())
        bodies.update(archive_data.keys())
        
        return jsonify({
            'success': True,
            'bodies': sorted(list(bodies))
        })
    except Exception as e:
        logger.error(f"Error in get_government_bodies: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search', methods=['GET'])
def search_documents():
    """Search across all documents"""
    try:
        query = request.args.get('q', '').lower()
        body_filter = request.args.get('body', '')
        type_filter = request.args.get('type', '')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter "q" is required'
            }), 400
        
        current_data = api_server.get_current_summaries()
        archive_data = api_server.get_historical_archive()
        
        results = []
        
        # Search current data
        for body_name, body_data in current_data.items():
            if body_filter and body_name != body_filter:
                continue
                
            for doc_type in ['agendas', 'minutes']:
                if type_filter and doc_type.rstrip('s') != type_filter:
                    continue
                    
                for doc in body_data.get(doc_type, []):
                    if (query in doc.get('title', '').lower() or 
                        query in doc.get('summary', '').lower()):
                        doc['source'] = 'current'
                        results.append(doc)
        
        # Search archive data
        for body_name, body_data in archive_data.items():
            if body_filter and body_name != body_filter:
                continue
                
            for doc_type in ['agendas', 'minutes']:
                if type_filter and doc_type.rstrip('s') != type_filter:
                    continue
                    
                for doc in body_data.get(doc_type, []):
                    if (query in doc.get('title', '').lower() or 
                        query in doc.get('summary', '').lower()):
                        doc['source'] = 'archive'
                        results.append(doc)
        
        # Sort by date (newest first)
        results.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        logger.error(f"Error in search_documents: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # For development
    app.run(host='0.0.0.0', port=5000, debug=True)

