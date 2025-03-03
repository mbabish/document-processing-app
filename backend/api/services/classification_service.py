import logging
import requests
import json
import re
import os

class ClassificationService:
    """
    Service responsible for classifying documents using an LLM API
    """
    def __init__(self, llm_api_url=None, schema_service=None):
        """
        Initialize the classification service
        
        :param llm_api_url: URL of the LLM API endpoint
        :param schema_service: Service to provide document schemas
        """
        # LLM API URL for text generation
        self.llm_api_url = llm_api_url or os.environ.get(
            'LLM_API_URL', 
            'http://localhost:8000'
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
        # If SchemaService is available, use its schemas
        if self.schema_service:
            try:
                schemas = self.schema_service.get_schemas()
                
                # Extract schema IDs if schemas exist
                if schemas:
                    return [schema['id'] for schema in schemas]
                
                # Log warning if no schemas found
                self.logger.warning("No schemas found in SchemaService")
            except Exception as e:
                self.logger.error(f"Error retrieving schemas: {str(e)}")
        
        # Fallback to a generic document type
        return ['generic']

    def _prepare_classification_prompt(self, text: str, document_types: list) -> str:
        """
        Prepare a prompt for document classification
        
        :param text: Text content to classify
        :param document_types: List of possible document types
        :return: Formatted classification prompt
        """
        # Truncate text to first 2000 characters
        text_to_classify = text[:2000]
        
        # Format document types for the prompt
        types_str = ', '.join(document_types)
        
        return f"""
        Analyze the following document text and determine its type. 
        Possible document types are: {types_str}.
        
        If you cannot confidently match the document to any of these types, 
        return 'generic' as the schema_id.
        
        Document text:
        {text_to_classify}
        
        Provide a JSON response with the following:
        {{
            "schema_id": "{types_str}/generic",
            "confidence": 0.0-1.0,
            "reasoning": "explanation",
            "extracted_data": {{
                "key1": "value1",
                "key2": "value2"
            }}
        }}
        
        Respond ONLY with the valid JSON, no additional text.
        """

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
            classification_prompt = self._prepare_classification_prompt(full_text, document_types)
            
            # Call LLM text generation endpoint
            response = requests.post(
                f"{self.llm_api_url}/api/generate", 
                json={
                    "prompt": classification_prompt,
                    "max_new_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30  # Add a timeout to prevent hanging
            )
            
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
                        
                        # Validate schema_id
                        if classification.get('schema_id') in document_types:
                            self.logger.info(f"Document classification: {classification}")
                            return classification
                    
                    # Fallback if JSON parsing fails
                    self.logger.warning(f"Failed to parse classification JSON: {generated_text}")
                except (json.JSONDecodeError, ValueError) as e:
                    self.logger.error(f"JSON parsing error: {str(e)}")
            
            # Fallback to generic classification
            return {
                "schema_id": "generic",
                "confidence": 0.0,
                "reasoning": "Classification failed",
                "extracted_data": None
            }
        
        except requests.RequestException as e:
            # Handle network or request errors
            self.logger.error(f"Classification request error: {str(e)}")
            return {
                "schema_id": "generic",
                "confidence": 0.0,
                "reasoning": f"Classification request error: {str(e)}",
                "extracted_data": None
            }

    def get_supported_document_types(self) -> list:
        """
        Get list of supported document types
        
        :return: List of document types
        """
        return self.get_document_types()