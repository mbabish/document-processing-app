import random
import datetime
import uuid

class DocumentService:
    def __init__(self):
        # Define available document schemas
        self.available_schemas = [
            {"id": "invoice", "title": "Invoice"},
            {"id": "receipt", "title": "Receipt"},
            {"id": "contract", "title": "Contract"}
        ]

    def process_document(self, original_filename, filepath):
        """
        Process an uploaded document and generate metadata.
        
        :param original_filename: Original name of the uploaded file
        :param filepath: Full path to the saved file
        :return: Dictionary with document metadata
        """
        # Randomly choose a schema for demonstration
        schema = random.choice(self.available_schemas)
        
        # Generate document metadata
        document = {
            "classification_id": f"doc-{uuid.uuid4()}",
            "filename": original_filename,
            "schema_id": schema["id"],
            "schema_title": schema["title"],
            "processed_at": datetime.datetime.now().isoformat(),
            "confidence": round(random.uniform(0.7, 0.99), 2),
            "fields_count": random.randint(5, 15),
            "filepath": filepath  # Caution: Be careful exposing this in production
        }
        
        return document

    def get_schemas(self):
        """
        Get available document schemas.
        
        :return: List of available schemas
        """
        return self.available_schemas