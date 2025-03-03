import datetime
from typing import Dict, List, Optional, Any

class ReportService:
    def __init__(self, document_service):
        """
        Initialize the report service with a document service.
        
        :param document_service: Service that manages document processing and retrieval
        """
        self.document_service = document_service

    def get_report(self, schema_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get report data for all documents or filtered by schema.
        
        :param schema_id: Optional schema ID to filter documents
        :return: Report data dictionary
        """
        # Get all documents
        documents = self.document_service.get_documents()
        
        # Get all available schemas
        available_schemas = self.document_service.get_schemas()
        
        # Prepare schema usage statistics
        schemas_used = self._calculate_schema_usage(documents, available_schemas)
        
        # If a specific schema is requested, filter documents
        if schema_id:
            documents = [
                doc for doc in documents 
                if doc.get('schema_id') == schema_id
            ]
            
            # If no documents found, but schema exists, return minimal report
            if not documents:
                if matching_schema:
                    return {
                        "generated_at": datetime.datetime.now().isoformat(),
                        "schema_id": schema_id,
                        "total_documents": 0,
                        "document_list": []
                    }
                return None
        
        # Construct the report
        report_data = {
            "generated_at": datetime.datetime.now().isoformat(),
            "total_documents": len(documents),
            "schemas_used": schemas_used,
            "document_list": documents
        }
        
        return report_data

    def _calculate_schema_usage(self, 
                                 documents: List[Dict[str, Any]], 
                                 available_schemas: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Calculate schema usage statistics, including schemas with zero documents.
        
        :param documents: List of processed documents
        :param available_schemas: List of all available schemas
        :return: Dictionary of schema usage statistics
        """
        # Count documents per schema
        schema_counts = {}
        for doc in documents:
            schema_id = doc.get('schema_id')
            
            if schema_id not in schema_counts:
                schema_counts[schema_id] = {
                    "count": 0,
                    "percentage": 0
                }
            
            schema_counts[schema_id]["count"] += 1
        
        # Prepare final schema usage statistics
        total_docs = len(documents)
        schemas_used = {}
        
        for schema in available_schemas:
            schema_id = schema['id']
            
            # Get count for this schema, default to 0 if no documents
            schema_info = schema_counts.get(schema_id, {"count": 0})
            
            schemas_used[schema_id] = {
                "title": schema['title'],
                "count": schema_info["count"],
                # Calculate percentage, handling zero total docs case
                "percentage": round((schema_info["count"] / total_docs * 100) if total_docs > 0 else 0, 1)
            }
        
        return schemas_used