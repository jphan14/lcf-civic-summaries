#!/usr/bin/env python3
"""
Production API Server Startup Script for QNAP
Handles CORS, logging, and production configuration
"""

import os
import sys
import logging
from datetime import datetime
from api_server import app

def setup_production_logging():
    """Set up production logging"""
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'api_server_{datetime.now().strftime("%Y%m%d")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def get_server_config():
    """Get server configuration"""
    config = {
        'host': '0.0.0.0',  # Allow external connections
        'port': int(os.environ.get('API_PORT', 5000)),
        'debug': os.environ.get('DEBUG', 'False').lower() == 'true'
    }
    
    return config

if __name__ == '__main__':
    setup_production_logging()
    logger = logging.getLogger(__name__)
    
    config = get_server_config()
    
    logger.info("Starting LCF Civic Summaries API Server")
    logger.info(f"Configuration: {config}")
    
    try:
        app.run(**config)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

