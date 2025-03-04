import random
import datetime
import uuid
import PyPDF2
import os
import logging
import json

class DocumentService:
    def __init__(self, classification_service=None, schema_service=None, storage_path=None):
        # Classification and schema services
        self.classification_service = classification_service
        self.schema_service = schema_service
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Configure document storage
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(__file__), 
            '../../_documents/processed_documents.json'
        )
        
        # Ensure storage file exists
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump([], f)
        
        # Internal storage of processed documents
        self._processed_documents = []
        self._load_processed_documents()

    def _load_processed_documents(self):
        """
        Load processed documents from storage file.
        """
        try:
            with open(self.storage_path, 'r') as f:
                self._processed_documents = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading processed documents: {str(e)}")
            self._processed_documents = []

    def _save_processed_documents(self):
        """
        Save processed documents to storage file.
        """
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self._processed_documents, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving processed documents: {str(e)}")

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
        else:
            # Find schema details
            schema = next((s for s in available_schemas if s['id'] == schema_id), 
                          available_schemas[0])
        
        # Generate document metadata
        document = {
            "classification_id": f"doc-{uuid.uuid4()}",
            "filename": original_filename,
            "schema_id": schema_id,
            "processed_at": datetime.datetime.now().isoformat(),
            "filepath": filepath,
            "parsed_content": parsed_content,
            "classification": classification,
            "confidence": classification.get('confidence', 0.5) if classification else 0.5
        }
        
        # Store the document locally
        self._processed_documents.append(document)
        
        # Save to persistent storage
        self._save_processed_documents()
        
        return document

    def get_documents(self, schema_id=None):
        """
        Retrieve processed documents, optionally filtered by schema.
        
        :param schema_id: Optional schema ID to filter documents
        :return: List of processed documents
        """

        # Always reload from disk to get fresh data
        self._load_processed_documents()

        if schema_id:
            return [
                doc for doc in self._processed_documents 
                if doc.get('schema_id') == schema_id
            ]
        return self._processed_documents

    def get_schemas(self):
        """
        Get available document schemas.
        
        :return: List of available schemas
        """
        return self.get_available_schemas()