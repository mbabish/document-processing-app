import logging
import uuid
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class SchemaService:
    """Service for managing document types"""
    
    def __init__(self):
        """
        Initialize the schema service with predefined document types
        """
        # Predefined document types
        self._predefined_types = [
            "Compliance Report",
            "Delivery Receipt",
            "Order",
            "Physician Notes", 
            "Prescription",
            "Sleep Study Report"
        ]
        
        # In-memory storage for schemas
        self._schemas = {
            str(uuid.uuid4()).replace('-', '')[:8]: {
                "id": str(uuid.uuid4()).replace('-', '')[:8],
                "title": doc_type
            } for doc_type in self._predefined_types
        }
    
    def get_schemas(self) -> List[Dict[str, Any]]:
        """
        Get list of available schemas
        
        Returns:
            List of schema metadata
        """
        return list(self._schemas.values())
    
    def get_schema(self, schema_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific schema by ID
        
        Args:
            schema_id: Schema identifier
            
        Returns:
            Schema object or None if not found
        """
        return self._schemas.get(schema_id)
    
    def add_schema(self, document_type: str) -> Tuple[bool, Optional[str]]:
        """
        Add a new document type
        
        Args:
            document_type: Name of the document type
            
        Returns:
            Tuple of (success, schema_id or error message)
        """
        # Check if document type already exists
        if any(schema['title'] == document_type for schema in self._schemas.values()):
            return False, f"Document type '{document_type}' already exists"
        
        # Generate a new schema ID
        schema_id = str(uuid.uuid4()).replace('-', '')[:8]
        
        # Create schema entry
        new_schema = {
            "id": schema_id,
            "title": document_type
        }
        
        # Add to schemas
        self._schemas[schema_id] = new_schema
        
        return True, schema_id
    
    def update_schema(self, schema_id: str, new_title: str) -> Tuple[bool, Optional[str]]:
        """
        Update an existing schema's title
        
        Args:
            schema_id: Schema identifier
            new_title: New title for the schema
            
        Returns:
            Tuple of (success, error message)
        """
        if schema_id not in self._schemas:
            return False, f"Schema {schema_id} not found"
        
        # Check if new title is unique
        if any(schema['title'] == new_title for schema in self._schemas.values() if schema['id'] != schema_id):
            return False, f"Document type '{new_title}' already exists"
        
        # Update the schema title
        self._schemas[schema_id]['title'] = new_title
        
        return True, None
    
    def delete_schema(self, schema_id: str) -> Tuple[bool, Optional[str]]:
        """
        Delete a schema
        
        Args:
            schema_id: Schema identifier
            
        Returns:
            Tuple of (success, error message)
        """
        if schema_id not in self._schemas:
            return False, f"Schema {schema_id} not found"
        
        # Prevent deletion of predefined types
        if any(self._schemas[schema_id]['title'] == doc_type for doc_type in self._predefined_types):
            return False, "Cannot delete predefined document types"
        
        # Remove the schema
        del self._schemas[schema_id]
        
        return True, None