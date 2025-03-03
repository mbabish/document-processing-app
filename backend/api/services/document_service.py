import random
import datetime
import uuid
import PyPDF2
import os
import logging

class DocumentService:
    def __init__(self, classification_service=None, schema_service=None):
        # Classification and schema services
        self.classification_service = classification_service
        self.schema_service = schema_service
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def parse_pdf_to_json(self, filepath):
        """
        Parse a PDF file and extract basic text content.
        
        :param filepath: Full path to the PDF file
        :return: Dictionary containing parsed PDF content
        """
        try:
            with open(filepath, 'rb') as file:
                # Use PyPDF2 to read the PDF
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Prepare a structured representation
                parsed_content = {
                    "metadata": {
                        "filename": filepath.split('/')[-1],
                        "parsed_at": datetime.datetime.now().isoformat(),
                        "total_pages": len(pdf_reader.pages)
                    },
                    "content": []
                }
                
                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    
                    page_data = {
                        "page_number": page_num + 1,
                        "text": page_text,
                        "length": len(page_text)
                    }
                    
                    parsed_content["content"].append(page_data)
            
            return parsed_content
        
        except Exception as e:
            # Log the error and return a basic error object
            self.logger.error(f"PDF parsing failed: {str(e)}")
            return {
                "error": "PDF parsing failed",
                "message": str(e)
            }

    def get_available_schemas(self):
        """
        Get available schemas from SchemaService.
        
        :return: List of available schemas
        """
        # Attempt to get schemas from SchemaService
        if self.schema_service:
            try:
                schemas = self.schema_service.get_schemas()
                
                # If no schemas are available from SchemaService
                if not schemas:
                    self.logger.warning("No schemas found in SchemaService")
                    return [
                        {"id": "generic", "title": "Generic Document"}
                    ]
                
                return schemas
            except Exception as e:
                self.logger.error(f"Error retrieving schemas: {str(e)}")
        
        # Absolute fallback if no SchemaService or retrieval fails
        return [
            {"id": "generic", "title": "Generic Document"}
        ]

    def process_document(self, original_filename, filepath):
        """
        Process an uploaded document and generate metadata.
        
        :param original_filename: Original name of the uploaded file
        :param filepath: Full path to the saved file
        :return: Dictionary with document metadata and parsed content
        """
        # Parse the PDF content
        parsed_content = self.parse_pdf_to_json(filepath)
        
        # Classify the document if classification service is available
        classification = None
        if self.classification_service:
            try:
                classification = self.classification_service.classify_document(parsed_content)
            except Exception as e:
                self.logger.error(f"Document classification error: {str(e)}")
        
        # Get available schemas
        available_schemas = self.get_available_schemas()
        
        # Determine schema
        schema_id = classification.get('schema_id') if classification else None
        if not schema_id:
            # Fallback to first available schema or generic
            schema = available_schemas[0]
            schema_id = schema['id']
            schema_title = schema['title']
        else:
            # Find schema details
            schema = next((s for s in available_schemas if s['id'] == schema_id), 
                          available_schemas[0])
            schema_title = schema['title']
        
        # Validate document if schema service is available
        validation_result = None
        if self.schema_service and classification and classification.get('extracted_data'):
            try:
                is_valid, error_message = self.schema_service.validate_document(
                    schema_id, 
                    classification['extracted_data']
                )
                validation_result = {
                    "is_valid": is_valid,
                    "error_message": error_message
                }
            except Exception as e:
                self.logger.error(f"Schema validation error: {str(e)}")
        
        # Generate document metadata
        document = {
            "classification_id": f"doc-{uuid.uuid4()}",
            "filename": original_filename,
            "schema_id": schema_id,
            "schema_title": schema_title,
            "processed_at": datetime.datetime.now().isoformat(),
            "fields_count": len(classification.get('extracted_data', {})) if classification else 0,
            "filepath": filepath,
            "parsed_content": parsed_content,
            "classification": classification,
            "validation": validation_result
        }
        
        return document

    def get_schemas(self):
        """
        Get available document schemas.
        
        :return: List of available schemas
        """
        return self.get_available_schemas()