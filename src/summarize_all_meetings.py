#!/usr/bin/env python3
"""
LCF Civic Summaries - AI Summarization
Railway-optimized version with environment variable configuration
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RailwaySummarizer:
    """Railway-optimized AI summarization with environment variable configuration."""
    
    def __init__(self):
        """Initialize the summarizer with Railway environment variables."""
        self.data_dir = os.getenv('DATA_DIR', 'data')
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        # OpenAI configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.max_tokens = int(os.getenv('MAX_TOKENS', '1000'))
        self.use_ai_summaries = os.getenv('USE_AI_SUMMARIES', 'true').lower() == 'true'
        
        # Rate limiting configuration
        self.max_api_calls = int(os.getenv('MAX_API_CALLS_PER_RUN', '20'))
        self.api_call_delay = float(os.getenv('API_CALL_DELAY', '2.0'))
        
        # Initialize OpenAI client if available
        self.openai_client = None
        if self.openai_api_key and self.use_ai_summaries:
            self.initialize_openai()
        
        # Create data directories
        os.makedirs(self.data_dir, exist_ok=True)
        
        logger.info(f"Summarizer initialized - Environment: {self.environment}")
        logger.info(f"AI summaries enabled: {self.use_ai_summaries}")
        logger.info(f"Max API calls per run: {self.max_api_calls}")
    
    def initialize_openai(self):
        """Initialize OpenAI client."""
        try:
            import openai
            
            # Try new OpenAI client first (v1.0+)
            try:
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                logger.info("OpenAI client initialized (v1.0+)")
            except AttributeError:
                # Fall back to older OpenAI library
                openai.api_key = self.openai_api_key
                self.openai_client = openai
                logger.info("OpenAI client initialized (legacy)")
                
        except ImportError:
            logger.error("OpenAI library not available")
            self.openai_client = None
        except Exception as e:
            logger.error(f"Error initializing OpenAI: {str(e)}")
            self.openai_client = None
    
    def load_documents(self) -> List[Dict[str, Any]]:
        """Load documents from metadata file."""
        metadata_file = os.path.join(self.data_dir, 'document_metadata.json')
        
        try:
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    documents = metadata.get('documents', [])
                    logger.info(f"Loaded {len(documents)} documents from metadata")
                    return documents
            else:
                logger.warning("No document metadata file found")
                return []
                
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            return []
    
    def create_ai_prompt(self, document: Dict[str, Any]) -> str:
        """Create AI prompt for document summarization."""
        doc_type = document.get('document_type', 'document')
        gov_body = document.get('government_body', 'Government Body')
        content = document.get('content', '')
        
        if doc_type == 'agenda':
            prompt = f"""Please provide a detailed summary of this {gov_body} meeting agenda. 
            
Focus on:
1. Key agenda items and topics to be discussed
2. Important decisions or votes scheduled
3. Public participation opportunities
4. Budget or financial matters
5. Community impact items
6. Any controversial or significant issues

Provide a comprehensive 3-4 paragraph summary that captures the main points and their significance to the La Cañada Flintridge community.

Agenda content:
{content[:4000]}"""  # Limit content to avoid token limits
        
        else:  # minutes
            prompt = f"""Please provide a detailed summary of this {gov_body} meeting minutes.
            
Focus on:
1. Key decisions made and votes taken
2. Important discussions and their outcomes
3. Public comments and community input
4. Budget approvals or financial decisions
5. Policy changes or new initiatives
6. Action items and next steps
7. Community impact of decisions made

Provide a comprehensive 3-4 paragraph summary that captures the main decisions, discussions, and their significance to the La Cañada Flintridge community.

Meeting minutes content:
{content[:4000]}"""  # Limit content to avoid token limits
        
        return prompt
    
    def call_openai_api(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Call OpenAI API with retry logic and rate limiting."""
        if not self.openai_client:
            return None
        
        for attempt in range(max_retries):
            try:
                # Add delay for rate limiting
                if attempt > 0:
                    delay = self.api_call_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying API call in {delay} seconds...")
                    time.sleep(delay)
                else:
                    time.sleep(self.api_call_delay)
                
                # Try new OpenAI client format first
                if hasattr(self.openai_client, 'chat'):
                    response = self.openai_client.chat.completions.create(
                        model=self.openai_model,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that summarizes government meeting documents for civic transparency."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=self.max_tokens,
                        temperature=0.3
                    )
                    return response.choices[0].message.content.strip()
                
                else:
                    # Legacy OpenAI format
                    response = self.openai_client.ChatCompletion.create(
                        model=self.openai_model,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that summarizes government meeting documents for civic transparency."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=self.max_tokens,
                        temperature=0.3
                    )
                    return response.choices[0].message.content.strip()
                
            except Exception as e:
                error_str = str(e).lower()
                
                if 'rate limit' in error_str or 'quota' in error_str:
                    logger.warning(f"Rate limit hit on attempt {attempt + 1}: {str(e)}")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        logger.error("Rate limit exceeded, max retries reached")
                        return None
                
                elif 'timeout' in error_str or 'connection' in error_str:
                    logger.warning(f"Connection issue on attempt {attempt + 1}: {str(e)}")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        logger.error("Connection issues, max retries reached")
                        return None
                
                else:
                    logger.error(f"OpenAI API error: {str(e)}")
                    return None
        
        return None
    
    def create_fallback_summary(self, document: Dict[str, Any]) -> str:
        """Create a fallback summary when AI is not available."""
        doc_type = document.get('document_type', 'document')
        gov_body = document.get('government_body', 'Government Body')
        content = document.get('content', '')
        date = document.get('date', 'Unknown date')
        
        # Extract key information from content
        content_preview = content[:500] + "..." if len(content) > 500 else content
        
        if doc_type == 'agenda':
            summary = f"""This {gov_body} meeting agenda for {date} contains important items for community consideration. 
            
The agenda includes various topics that will be discussed during the upcoming meeting. Community members are encouraged to review the full agenda and participate in the public comment period if interested in any of the items.

Key areas typically covered include administrative matters, public hearings, policy discussions, and community development issues. The full agenda document provides detailed information about each item, including background materials and staff recommendations.

Preview of agenda content: {content_preview}"""
        
        else:  # minutes
            summary = f"""These {gov_body} meeting minutes from {date} document the decisions and discussions from the meeting.
            
The minutes record the official actions taken by the {gov_body}, including any votes, approvals, and policy decisions made during the session. Public comments and community input are also documented as part of the official record.

These minutes serve as the permanent record of the meeting and are important for tracking the progress of various municipal matters and community initiatives over time.

Preview of minutes content: {content_preview}"""
        
        return summary
    
    def summarize_document(self, document: Dict[str, Any], api_call_count: int) -> Dict[str, Any]:
        """Summarize a single document."""
        doc_id = f"{document.get('government_body', 'Unknown')}_{document.get('document_type', 'doc')}_{document.get('date', 'unknown')}"
        
        logger.info(f"Summarizing document: {doc_id}")
        
        # Check if we've exceeded API call limit
        if api_call_count >= self.max_api_calls:
            logger.warning(f"API call limit reached ({self.max_api_calls}), using fallback summary")
            summary = self.create_fallback_summary(document)
            ai_generated = False
        
        # Try AI summarization if available and within limits
        elif self.openai_client and self.use_ai_summaries:
            prompt = self.create_ai_prompt(document)
            ai_summary = self.call_openai_api(prompt)
            
            if ai_summary:
                summary = ai_summary
                ai_generated = True
                logger.info(f"Generated AI summary for {doc_id}")
            else:
                logger.warning(f"AI summarization failed for {doc_id}, using fallback")
                summary = self.create_fallback_summary(document)
                ai_generated = False
        
        else:
            # Use fallback summary
            summary = self.create_fallback_summary(document)
            ai_generated = False
            logger.info(f"Generated fallback summary for {doc_id}")
        
        # Create summary object
        summary_obj = {
            'government_body': document.get('government_body', 'Unknown'),
            'document_type': document.get('document_type', 'document'),
            'date': document.get('date', 'Unknown'),
            'title': document.get('title', 'Untitled Document'),
            'url': document.get('url', ''),
            'summary': summary,
            'ai_generated': ai_generated,
            'created_at': datetime.now().isoformat(),
            'model_used': self.openai_model if ai_generated else 'fallback',
            'manual_document': document.get('manual', False),
            'mock_document': document.get('mock', False)
        }
        
        return summary_obj
    
    def save_summaries(self, summaries: List[Dict[str, Any]]):
        """Save summaries to JSON file."""
        summaries_file = os.path.join(self.data_dir, 'document_summaries.json')
        
        summary_data = {
            'last_updated': datetime.now().isoformat(),
            'total_summaries': len(summaries),
            'ai_summaries': len([s for s in summaries if s.get('ai_generated', False)]),
            'fallback_summaries': len([s for s in summaries if not s.get('ai_generated', False)]),
            'summaries': summaries
        }
        
        try:
            with open(summaries_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, default=str)
            
            logger.info(f"Saved {len(summaries)} summaries to {summaries_file}")
            
        except Exception as e:
            logger.error(f"Error saving summaries: {str(e)}")
    
    def summarize_all_documents(self):
        """Main method to summarize all documents."""
        logger.info("=== Starting Document Summarization Process ===")
        
        # Load documents
        documents = self.load_documents()
        
        if not documents:
            logger.warning("No documents found to summarize")
            return {
                'total_summaries': 0,
                'ai_summaries': 0,
                'fallback_summaries': 0,
                'summaries': []
            }
        
        summaries = []
        api_call_count = 0
        
        # Process each document
        for i, document in enumerate(documents):
            try:
                summary = self.summarize_document(document, api_call_count)
                summaries.append(summary)
                
                # Increment API call count if AI was used
                if summary.get('ai_generated', False):
                    api_call_count += 1
                
                logger.info(f"Processed document {i + 1}/{len(documents)}")
                
            except Exception as e:
                logger.error(f"Error summarizing document {i + 1}: {str(e)}")
                continue
        
        # Save summaries
        self.save_summaries(summaries)
        
        ai_count = len([s for s in summaries if s.get('ai_generated', False)])
        fallback_count = len(summaries) - ai_count
        
        logger.info(f"=== Summarization Complete ===")
        logger.info(f"Total summaries: {len(summaries)}")
        logger.info(f"AI summaries: {ai_count}")
        logger.info(f"Fallback summaries: {fallback_count}")
        logger.info(f"API calls used: {api_call_count}/{self.max_api_calls}")
        
        return {
            'total_summaries': len(summaries),
            'ai_summaries': ai_count,
            'fallback_summaries': fallback_count,
            'api_calls_used': api_call_count,
            'summaries': summaries
        }

def main():
    """Main function for Railway deployment."""
    try:
        summarizer = RailwaySummarizer()
        result = summarizer.summarize_all_documents()
        
        logger.info("Document summarization completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Document summarization failed: {str(e)}")
        raise

if __name__ == '__main__':
    main()

