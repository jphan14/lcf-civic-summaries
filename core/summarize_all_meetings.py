#!/usr/bin/env python3
"""
La Canada Flintridge Government Meetings Tracker - Document Summarizer
Generates AI-powered summaries of meeting documents with enhanced detail.
"""

import os
import sys
import json
import logging
from datetime import datetime
import openai
import PyPDF2
from io import StringIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lcf_government_summarizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MeetingSummarizer:
    """Generates AI summaries of meeting documents."""
    
    def __init__(self, config_path="config.json"):
        """Initialize the summarizer with configuration."""
        config = self.load_config(config_path)
        self.config = {
            "use_ai_summaries": config.get("use_ai_summaries", True),
            "openai_api_key": config.get("openai_api_key"),
            "summary_style": "detailed",
            "max_tokens": 1000,  # Increased from 500 to 1000 for longer summaries
            "temperature": 0.3
        }
        self.setup_openai()
    
    def load_config(self, config_path):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found. Using default settings.")
            return self.get_default_config()
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file {config_path}. Using default settings.")
            return self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration."""
        return {
            "use_ai_summaries": True,
            "openai_api_key": None,
            "summary_style": "detailed",
            "max_tokens": 1000,
            "temperature": 0.3
        }
    
    def setup_openai(self):
        """Set up OpenAI API client."""
        api_key = self.config.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OpenAI API key not found in config or environment variables")
            self.openai_available = False
            return
        
        try:
            # Set up OpenAI client for both old and new versions
            if hasattr(openai, 'OpenAI'):
                # New OpenAI v1.0+ API
                self.openai_client = openai.OpenAI(api_key=api_key)
                # Test the API key with a simple request
                self.openai_client.models.list()
            else:
                # Old OpenAI API
                openai.api_key = api_key
                # Test the API key with a simple request
                openai.Model.list()
                self.openai_client = None
            
            self.openai_available = True
            logger.info("OpenAI API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI API: {e}")
            self.openai_available = False
            self.openai_client = None
    
    def extract_text_from_file(self, file_path):
        """Extract text content from a file (PDF or text)."""
        try:
            # Check file extension
            if file_path.lower().endswith('.pdf'):
                return self.extract_text_from_pdf(file_path)
            else:
                # Assume it's a text file
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
                    
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return None
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text content from a PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                return text.strip()
                
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return None
    
    def get_summary_prompt(self, document_type, body_name, document_text):
        """Generate a detailed prompt for AI summarization."""
        prompt = f"""Please provide a comprehensive and detailed summary of this {document_type} from the {body_name}. 

The summary should be 3-4 paragraphs long and include:

1. **Main Topics & Decisions**: Key agenda items, motions, votes, and decisions made
2. **Important Details**: Specific dollar amounts, dates, locations, and names mentioned
3. **Public Input**: Any public comments, concerns, or community feedback discussed
4. **Action Items**: Next steps, deadlines, future meetings, or follow-up actions required
5. **Context & Impact**: How these decisions might affect residents or the community

Please write in clear, accessible language that residents can easily understand. Focus on information that would be most relevant to community members who want to stay informed about local government activities.

Document content:
{document_text}

Provide a detailed summary that captures the substance and significance of this meeting:"""
        
        return prompt
    
    def generate_ai_summary(self, document_type, body_name, document_text, document_url=None):
        """Generate an AI summary of the document."""
        if not self.openai_available:
            return self.generate_fallback_summary(document_type, body_name, document_text)
        
        try:
            prompt = self.get_summary_prompt(document_type, body_name, document_text)
            
            # Truncate text if too long (OpenAI has token limits)
            max_chars = 15000  # Increased limit for longer documents
            if len(document_text) > max_chars:
                document_text = document_text[:max_chars] + "...\n[Document truncated due to length]"
                prompt = self.get_summary_prompt(document_type, body_name, document_text)
            
            # Use appropriate API based on OpenAI version
            if self.openai_client:
                # New OpenAI v1.0+ API
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that creates detailed, comprehensive summaries of government meeting documents for community members. Focus on clarity, completeness, and relevance to residents."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.config.get("max_tokens", 1000),
                    temperature=self.config.get("temperature", 0.3)
                )
                summary = response.choices[0].message.content.strip()
            else:
                # Old OpenAI API
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that creates detailed, comprehensive summaries of government meeting documents for community members. Focus on clarity, completeness, and relevance to residents."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.config.get("max_tokens", 1000),
                    temperature=self.config.get("temperature", 0.3)
                )
                summary = response.choices[0].message.content.strip()
            
            logger.info(f"Generated detailed AI summary for {body_name} {document_type}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            return self.generate_fallback_summary(document_type, body_name, document_text)
    
    def generate_fallback_summary(self, document_type, body_name, document_text):
        """Generate a fallback summary when AI is not available."""
        logger.info(f"Generating fallback summary for {body_name} {document_type}")
        
        # Extract key information using simple text processing
        lines = document_text.split('\n')
        important_lines = []
        
        # Look for lines that might contain important information
        keywords = [
            'motion', 'vote', 'approved', 'denied', 'budget', 'funding',
            'public comment', 'discussion', 'action item', 'next meeting',
            'resolution', 'ordinance', 'permit', 'development', 'project'
        ]
        
        for line in lines:
            line = line.strip()
            if len(line) > 20:  # Skip very short lines
                for keyword in keywords:
                    if keyword.lower() in line.lower():
                        important_lines.append(line)
                        break
        
        # Create a basic summary
        if important_lines:
            summary = f"This {document_type} from the {body_name} covers several important topics. "
            summary += "Key items discussed include: " + ". ".join(important_lines[:5])
            if len(important_lines) > 5:
                summary += f" and {len(important_lines) - 5} additional items."
        else:
            summary = f"This {document_type} from the {body_name} contains meeting information and agenda items. Please refer to the full document for complete details."
        
        return summary
    
    def summarize_documents(self, documents_data):
        """Summarize all documents in the provided data structure."""
        summaries = {}
        
        for body_name, body_data in documents_data.items():
            logger.info(f"Processing summaries for {body_name}")
            summaries[body_name] = {
                "agendas": [],
                "minutes": []
            }
            
            # Process agendas
            for agenda in body_data.get("agendas", []):
                try:
                    # Extract text from file if available
                    text_content = agenda.get("text_content", "")
                    if not text_content and agenda.get("local_path"):
                        text_content = self.extract_text_from_file(agenda["local_path"])
                    
                    if text_content:
                        summary = self.generate_ai_summary(
                            "agenda", 
                            body_name, 
                            text_content,
                            agenda.get("url")
                        )
                        
                        summaries[body_name]["agendas"].append({
                            "title": agenda.get("title", "Meeting Agenda"),
                            "date": agenda.get("date"),
                            "url": agenda.get("url", ""),
                            "summary": summary,
                            "ai_generated": self.openai_available,
                            "type": "agenda"
                        })
                    else:
                        logger.warning(f"No text content available for {body_name} agenda")
                        
                except Exception as e:
                    logger.error(f"Error processing agenda for {body_name}: {e}")
            
            # Process minutes
            for minute in body_data.get("minutes", []):
                try:
                    # Extract text from file if available
                    text_content = minute.get("text_content", "")
                    if not text_content and minute.get("local_path"):
                        text_content = self.extract_text_from_file(minute["local_path"])
                    
                    if text_content:
                        summary = self.generate_ai_summary(
                            "minutes", 
                            body_name, 
                            text_content,
                            minute.get("url")
                        )
                        
                        summaries[body_name]["minutes"].append({
                            "title": minute.get("title", "Meeting Minutes"),
                            "date": minute.get("date"),
                            "url": minute.get("url", ""),
                            "summary": summary,
                            "ai_generated": self.openai_available,
                            "type": "minutes"
                        })
                    else:
                        logger.warning(f"No text content available for {body_name} minutes")
                        
                except Exception as e:
                    logger.error(f"Error processing minutes for {body_name}: {e}")
        
        # Save summaries to file with proper JSON serialization
        output_file = "document_summaries.json"
        with open(output_file, 'w') as f:
            json.dump(summaries, f, indent=2, default=str)
        
        logger.info(f"Summaries saved to {output_file}")
        return summaries

def main():
    """Main entry point for the script."""
    try:
        # Load documents data
        documents_file = "documents_data.json"
        if not os.path.exists(documents_file):
            logger.error(f"Documents file {documents_file} not found. Run fetch_all_meetings.py first.")
            return False
        
        with open(documents_file, 'r') as f:
            documents_data = json.load(f)
        
        # Initialize summarizer and process documents
        summarizer = MeetingSummarizer()
        summaries = summarizer.summarize_documents(documents_data)
        
        # Print summary statistics
        total_summaries = 0
        for body_data in summaries.values():
            total_summaries += len(body_data.get("agendas", []))
            total_summaries += len(body_data.get("minutes", []))
        
        logger.info(f"Successfully generated {total_summaries} detailed summaries")
        return True
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

