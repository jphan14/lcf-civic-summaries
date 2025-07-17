from flask import Blueprint, jsonify
import json
import os
from datetime import datetime
from .integration import TrackerIntegration

summaries_bp = Blueprint('summaries', __name__)

@summaries_bp.route('/summaries', methods=['GET'])
def get_summaries():
    """Get current government meeting summaries."""
    try:
        integration = TrackerIntegration()
        result = integration.get_website_data()
        
        if result["success"]:
            return jsonify({
                "success": True,
                "data": result["data"],
                "metadata": result.get("metadata", {}),
                "last_updated": result.get("metadata", {}).get("last_updated", datetime.now().isoformat())
            })
        else:
            # Fallback to mock data if no real data is available
            mock_data = {
                "City Council": {
                    "agendas": [
                        {
                            "title": "City Council Regular Meeting Agenda",
                            "type": "agenda",
                            "date": "2025-07-15T19:00:00",
                            "summary": "The upcoming City Council meeting will address several key items including the annual budget review, proposed traffic calming measures on Foothill Boulevard, and updates on the Community Center renovation project. Public comment period scheduled for 7:30 PM.",
                            "ai_generated": True,
                            "url": "https://lcf.ca.gov/agendas/city_council_20250715.pdf"
                        }
                    ],
                    "minutes": [
                        {
                            "title": "City Council Regular Meeting Minutes",
                            "type": "minutes", 
                            "date": "2025-07-08T19:00:00",
                            "summary": "Council approved the $2.3M budget allocation for street improvements, unanimously passed Resolution 2025-15 regarding noise ordinance updates, and received presentations on the new recycling program. Mayor Johnson announced the upcoming town hall on housing development.",
                            "ai_generated": True,
                            "url": "https://lcf.ca.gov/minutes/city_council_20250708.pdf"
                        }
                    ]
                },
                "Planning Commission": {
                    "agendas": [
                        {
                            "title": "Planning Commission Meeting Agenda",
                            "type": "agenda",
                            "date": "2025-07-14T18:00:00",
                            "summary": "Review of three residential development proposals, discussion of updated zoning guidelines for hillside properties, and consideration of the General Plan Housing Element update. Site visit scheduled for the Oakwood development project.",
                            "ai_generated": True,
                            "url": "https://lcf.ca.gov/agendas/planning_commission_20250714.pdf"
                        }
                    ],
                    "minutes": [
                        {
                            "title": "Planning Commission Meeting Minutes",
                            "type": "minutes",
                            "date": "2025-07-07T18:00:00", 
                            "summary": "Commission approved the conditional use permit for the new medical office building on Foothill Boulevard with conditions regarding parking and landscaping. Denied the variance request for 1234 Oak Street due to setback concerns.",
                            "ai_generated": True,
                            "url": "https://lcf.ca.gov/minutes/planning_commission_20250707.pdf"
                        }
                    ]
                },
                "Public Safety Commission": {
                    "agendas": [
                        {
                            "title": "Public Safety Commission Agenda",
                            "type": "agenda",
                            "date": "2025-07-13T17:00:00",
                            "summary": "Discussion of emergency preparedness protocols, review of recent fire safety inspections, and presentation on the new neighborhood watch program. Update on traffic enforcement initiatives and pedestrian safety measures.",
                            "ai_generated": False,
                            "url": "https://lcf.ca.gov/agendas/public_safety_commission_20250713.pdf"
                        }
                    ],
                    "minutes": [
                        {
                            "title": "Public Safety Commission Minutes", 
                            "type": "minutes",
                            "date": "2025-07-06T17:00:00",
                            "summary": "Commission reviewed quarterly crime statistics showing a 15% decrease in property crimes. Approved funding for additional emergency communication equipment and discussed coordination with LA County Fire Department for wildfire prevention.",
                            "ai_generated": False,
                            "url": "https://lcf.ca.gov/minutes/public_safety_commission_20250706.pdf"
                        }
                    ]
                }
            }
            
            return jsonify({
                "success": True,
                "data": mock_data,
                "last_updated": datetime.now().isoformat(),
                "note": "Using mock data - tracker system not yet integrated"
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@summaries_bp.route('/archive', methods=['GET'])
def get_historical_archive():
    """Get historical archive data for 2025."""
    try:
        integration = TrackerIntegration()
        result = integration.get_historical_archive()
        
        if result["success"]:
            return jsonify({
                "success": True,
                "data": result["data"],
                "metadata": result.get("metadata", {}),
                "last_updated": result.get("metadata", {}).get("last_updated", datetime.now().isoformat())
            })
        else:
            # Fallback to mock historical data
            mock_historical_data = {
                "City Council": {
                    "agendas": [
                        {
                            "title": "City Council Agenda - June 21, 2025",
                            "type": "agenda",
                            "date": "2025-06-21T19:00:00",
                            "month": "June 2025",
                            "year": 2025,
                            "summary": "Budget workshop session focusing on the FY 2025-26 proposed budget. Discussion of capital improvement projects including street resurfacing, park upgrades, and technology infrastructure improvements. Public hearing on proposed fee schedule updates.",
                            "ai_generated": True,
                            "historical": True,
                            "url": "https://lcf.ca.gov/agendas/city_council_20250621.pdf"
                        },
                        {
                            "title": "City Council Agenda - June 07, 2025",
                            "type": "agenda",
                            "date": "2025-06-07T19:00:00",
                            "month": "June 2025",
                            "year": 2025,
                            "summary": "Regular meeting agenda including consideration of the Community Development Block Grant allocation, updates on the Foothill Boulevard streetscape project, and discussion of the new municipal code regarding short-term rentals.",
                            "ai_generated": True,
                            "historical": True,
                            "url": "https://lcf.ca.gov/agendas/city_council_20250607.pdf"
                        }
                    ],
                    "minutes": [
                        {
                            "title": "City Council Minutes - June 14, 2025",
                            "type": "minutes",
                            "date": "2025-06-14T19:00:00",
                            "month": "June 2025",
                            "year": 2025,
                            "summary": "Council unanimously approved the $15.2M annual budget with amendments to increase funding for road maintenance and public safety equipment. Approved the contract for the new library management system and received updates on the Climate Action Plan implementation.",
                            "ai_generated": True,
                            "historical": True,
                            "url": "https://lcf.ca.gov/minutes/city_council_20250614.pdf"
                        }
                    ]
                },
                "Planning Commission": {
                    "agendas": [
                        {
                            "title": "Planning Commission Agenda - June 16, 2025",
                            "type": "agenda",
                            "date": "2025-06-16T18:00:00",
                            "month": "June 2025",
                            "year": 2025,
                            "summary": "Review of the proposed mixed-use development at 1500 Foothill Boulevard, consideration of amendments to the hillside development ordinance, and discussion of the Housing Element annual progress report.",
                            "ai_generated": True,
                            "historical": True,
                            "url": "https://lcf.ca.gov/agendas/planning_commission_20250616.pdf"
                        }
                    ],
                    "minutes": [
                        {
                            "title": "Planning Commission Minutes - June 02, 2025",
                            "type": "minutes",
                            "date": "2025-06-02T18:00:00",
                            "month": "June 2025",
                            "year": 2025,
                            "summary": "Commission approved the conditional use permit for the expanded medical facility with conditions for enhanced landscaping and traffic management. Continued the hearing for the Oak Grove residential project pending additional environmental review.",
                            "ai_generated": True,
                            "historical": True,
                            "url": "https://lcf.ca.gov/minutes/planning_commission_20250602.pdf"
                        }
                    ]
                }
            }
            
            return jsonify({
                "success": True,
                "data": mock_historical_data,
                "last_updated": datetime.now().isoformat(),
                "note": "Using mock historical data - archive system not yet fully integrated"
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@summaries_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "LCF Civic Summaries API",
        "timestamp": datetime.now().isoformat()
    })

