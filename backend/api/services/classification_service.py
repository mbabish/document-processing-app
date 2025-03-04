import logging
import requests
import json
import re
import os

class ClassificationService:
    """
    Service responsible for classifying documents using an LLM API
    """
    def __init__(self, schema_service=None):
        """
        Initialize the classification service
        
        :param llm_api_url: URL of the LLM API endpoint
        :param schema_service: Service to provide document schemas
        """
        # LLM API URL for text generation
        self.llm_api_url = os.environ.get(
            'LLM_API_URL', 
            'http://llm:8000'
        )
        
        # Schema service
        self.schema_service = schema_service
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_document_types(self):
        """
        Get available document types from SchemaService
        
        :return: List of document types
        """
        if self.schema_service:
            try:
                schemas = self.schema_service.get_schemas()
                
                # Extract schema titles if schemas exist
                if schemas:
                    return [schema['title'] for schema in schemas]
                
                # Log warning if no schemas found
                self.logger.warning("No schemas found in SchemaService")
            except Exception as e:
                self.logger.error(f"Error retrieving schemas: {str(e)}")
        
        return []

    def classify_document(self, parsed_content: dict) -> dict:
        """
        Classify a document using LLM text generation API
        
        :param parsed_content: Parsed PDF content
        :return: Classification result
        """
        # Get available document types
        document_types = self.get_document_types()
        
        try:
            # Prepare the text for classification
            full_text = " ".join([page['text'] for page in parsed_content.get('content', [])])
            
            # Prepare classification prompt
            classification_prompt = f"""
Analyze the following document text and determine its type. 
Possible document types are: {', '.join(document_types)}.

Provide a JSON response in the following format with no additional text:
{{
    "schema_id": "chosen document type",
    "reasoning": "explanation"
}}

The document text will start and end with "==========" but could be empty:
==========
{full_text[:2000]}
==========
"""
            
            self.logger.info(f"Classification Prompt: {classification_prompt}")


            # Call LLM text generation endpoint
            response = requests.post(
                f"{self.llm_api_url}/api/generate", 
                json={
                    "prompt": classification_prompt,
                    "max_new_tokens": 500,
                    "temperature": 0.7
                },
                timeout=120  # Add a timeout to prevent hanging
            )

            self.logger.info(f"Response Text: {response.text}")

            # Check if request was successful
            if response.status_code == 200:

                # Extract the generated text
                generated_text = response.json().get('text', '')
                
                # Try to extract JSON from the generated text
                try:
                    # Use regex to extract JSON
                    json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
                    if json_match:
                        classification = json.loads(json_match.group(0))
                        
                        # Validate and fallback if needed
                        schema_id = classification.get('schema_id', '')
                        if schema_id not in document_types:
                            schema_id = 'Generic Document'
                        
                        # Ensure confidence is within 0-1 range
                        confidence = max(0, min(1, classification.get('confidence', 0.5)))
                        
                        return {
                            "schema_id": schema_id,
                            "reasoning": classification.get('reasoning', 'Classification based on document content')
                        }
                    
                    # Fallback if JSON parsing fails
                    self.logger.warning(f"Failed to parse classification JSON: {generated_text}")
                except (json.JSONDecodeError, ValueError) as e:
                    self.logger.error(f"JSON parsing error: {str(e)}")
            
            # Fallback to generic classification
            return {
                "schema_id": "Generic Document",
                "confidence": 0.5,
                "reasoning": "Unable to classify document"
            }
        
        except requests.RequestException as e:
            # Handle network or request errors
            self.logger.error(f"Classification request error: {str(e)}")
            return {
                "schema_id": "Generic Document",
                "reasoning": f"Classification request error: {str(e)}"
            }

    def get_supported_document_types(self) -> list:
        """
        Get list of supported document types
        
        :return: List of document types
        """
        return self.get_document_types()