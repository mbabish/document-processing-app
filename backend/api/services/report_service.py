import random
import datetime

class ReportService:
    def __init__(self, document_service):
        self.document_service = document_service

    def generate_mock_data(self, num_documents=20):
        """
        Generate mock report data for demonstration purposes.
        
        :param num_documents: Number of mock documents to generate
        :return: Dictionary with mock report data
        """
        # Get available schemas
        schemas = self.document_service.get_schemas()
        schema_ids = [schema["id"] for schema in schemas]
        schema_titles = {schema["id"]: schema["title"] for schema in schemas}
        
        # Generate mock documents
        documents = []
        for i in range(num_documents):
            schema = random.choice(schemas)
            documents.append({
                "classification_id": f"doc-{i+1}",
                "filename": f"document_{i+1}.pdf",
                "schema_id": schema["id"],
                "schema_title": schema["title"],
                "processed_at": (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))).isoformat(),
                "confidence": round(random.uniform(0.7, 0.99), 2),
                "fields_count": random.randint(5, 15)
            })
        
        # Calculate schema usage stats
        schema_counts = {schema_id: 0 for schema_id in schema_ids}
        for doc in documents:
            schema_counts[doc["schema_id"]] += 1
        
        schemas_used = {}
        for schema_id, count in schema_counts.items():
            schemas_used[schema_id] = {
                "title": schema_titles[schema_id],
                "count": count,
                "percentage": round((count / len(documents)) * 100, 1)
            }
        
        # Mock field coverage
        field_coverage = self._generate_field_coverage(schema_ids)
        
        return {
            "generated_at": datetime.datetime.now().isoformat(),
            "total_documents": len(documents),
            "schemas_used": schemas_used,
            "field_coverage": field_coverage,
            "recent_classifications": documents[:5],
            "document_list": documents
        }

    def _generate_field_coverage(self, schema_ids):
        """
        Generate mock field coverage data.
        
        :param schema_ids: List of schema IDs
        :return: Dictionary with field coverage data
        """
        field_coverage = {}
        for schema_id in schema_ids:
            fields = {
                "total": {"count": random.randint(40, 50), "total": 50, "coverage": 0},
                "date": {"count": random.randint(15, 20), "total": 20, "coverage": 0},
                "amount": {"count": random.randint(15, 20), "total": 20, "coverage": 0}
            }
            
            # Calculate coverage percentages
            for field in fields:
                fields[field]["coverage"] = round((fields[field]["count"] / fields[field]["total"]) * 100, 1)
            
            field_coverage[schema_id] = {
                "fields": fields,
                "overall_coverage": round(sum(f["count"] for f in fields.values()) / sum(f["total"] for f in fields.values()) * 100, 1)
            }
        
        return field_coverage

    def get_report(self, schema_id=None):
        """
        Get report data, optionally filtered by schema.
        
        :param schema_id: Optional schema ID to filter documents
        :return: Report data dictionary
        """
        mock_data = self.generate_mock_data()
        
        # If no schema_id is provided, return full data
        if not schema_id:
            return mock_data
        
        # Filter documents by schema_id
        documents = [doc for doc in mock_data["document_list"] if doc["schema_id"] == schema_id]
        
        if not documents:
            return None
        
        # Create schema-specific report
        schema_report = {
            "generated_at": mock_data["generated_at"],
            "schema_id": schema_id,
            "schema_title": documents[0]["schema_title"],
            "total_documents": len(documents),
            "field_coverage": {schema_id: mock_data["field_coverage"].get(schema_id, {})},
            "document_list": documents
        }
        
        return schema_report