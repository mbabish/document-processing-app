import os
import json
import logging
import jsonschema
from jsonschema import validate, ValidationError
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class SchemaService:
    """Service for managing and validating JSON schemas for document classifications"""
    
    def __init__(self, schemas_dir: str = None):
        """
        Initialize the schema service
        
        Args:
            schemas_dir: Directory path for JSON schema files
        """
        self.schemas_dir = schemas_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'schemas')
        self.schemas = {}
        self._load_schemas()
    
    def _load_schemas(self) -> None:
        """Load all schema files from the schemas directory"""
        os.makedirs(self.schemas_dir, exist_ok=True)
        
        # Clear existing schemas
        self.schemas = {}
        
        # Load schemas from files
        for filename in os.listdir(self.schemas_dir):
            if filename.endswith('.json') and not filename.startswith('.'):
                schema_id = os.path.splitext(filename)[0]
                filepath = os.path.join(self.schemas_dir, filename)
                
                try:
                    with open(filepath, 'r') as f:
                        schema = json.load(f)
                        # Validate that it's a valid JSON schema
                        jsonschema.Draft7Validator.check_schema(schema)
                        self.schemas[schema_id] = schema
                        logger.info(f"Loaded schema: {schema_id}")
                except Exception as e:
                    logger.error(f"Error loading schema {schema_id}: {str(e)}")
    
    def get_schemas(self) -> List[Dict[str, Any]]:
        """
        Get list of available schemas
        
        Returns:
            List of schema metadata
        """
        return [
            {
                "id": schema_id,
                "title": schema.get("title", schema_id),
                "description": schema.get("description", ""),
                "version": schema.get("version", "1.0")
            }
            for schema_id, schema in self.schemas.items()
        ]
    
    def get_schema(self, schema_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific schema by ID
        
        Args:
            schema_id: Schema identifier
            
        Returns:
            Schema object or None if not found
        """
        return self.schemas.get(schema_id)
    
    def validate_document(self, schema_id: str, document: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate a document against a schema
        
        Args:
            schema_id: Schema identifier
            document: Document data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        schema = self.get_schema(schema_id)
        if not schema:
            return False, f"Schema {schema_id} not found"
        
        try:
            validate(instance=document, schema=schema)
            return True, None
        except ValidationError as e:
            return False, str(e)
    
    def add_schema(self, schema_id: str, schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Add a new schema
        
        Args:
            schema_id: Schema identifier
            schema: Schema definition
            
        Returns:
            Tuple of (success, error_message)
        """
        # Validate it's a valid JSON schema
        try:
            jsonschema.Draft7Validator.check_schema(schema)
        except Exception as e:
            return False, f"Invalid JSON schema: {str(e)}"
        
        # Save to file
        filepath = os.path.join(self.schemas_dir, f"{schema_id}.json")
        try:
            with open(filepath, 'w') as f:
                json.dump(schema, f, indent=2)
            
            # Add to in-memory cache
            self.schemas[schema_id] = schema
            return True, None
        except Exception as e:
            return False, f"Error saving schema: {str(e)}"
    
    def update_schema(self, schema_id: str, schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Update an existing schema
        
        Args:
            schema_id: Schema identifier
            schema: New schema definition
            
        Returns:
            Tuple of (success, error_message)
        """
        if schema_id not in self.schemas:
            return False, f"Schema {schema_id} not found"
        
        return self.add_schema(schema_id, schema)
    
    def delete_schema(self, schema_id: str) -> Tuple[bool, Optional[str]]:
        """
        Delete a schema
        
        Args:
            schema_id: Schema identifier
            
        Returns:
            Tuple of (success, error_message)
        """
        if schema_id not in self.schemas:
            return False, f"Schema {schema_id} not found"
        
        filepath = os.path.join(self.schemas_dir, f"{schema_id}.json")
        try:
            os.remove(filepath)
            del self.schemas[schema_id]
            return True, None
        except Exception as e:
            return False, f"Error deleting schema: {str(e)}"