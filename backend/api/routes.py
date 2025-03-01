from flask import Blueprint, jsonify
import datetime
import random

api_bp = Blueprint('api', __name__)

# Mock data for demonstration purposes
def generate_mock_data():
    schema_ids = ["invoice", "receipt", "contract", "test"]
    schema_titles = {"invoice": "Invoice", "receipt": "Receipt", "contract": "Contract", "test": "Test"}
    
    documents = []
    for i in range(20):
        schema_id = random.choice(schema_ids)
        documents.append({
            "classification_id": f"doc-{i+1}",
            "filename": f"document_{i+1}.pdf",
            "schema_id": schema_id,
            "schema_title": schema_titles[schema_id],
            "processed_at": (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))).isoformat(),
            "confidence": round(random.uniform(0.6, 0.99), 2),
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
    
    # Mock confidence metrics
    confidence_values = [doc["confidence"] for doc in documents]
    confidence_by_schema = {}
    
    for schema_id in schema_ids:
        schema_confidences = [doc["confidence"] for doc in documents if doc["schema_id"] == schema_id]
        if schema_confidences:
            confidence_by_schema[schema_id] = {
                "average": round(sum(schema_confidences) / len(schema_confidences), 2),
                "median": round(sorted(schema_confidences)[len(schema_confidences) // 2], 2),
                "min": round(min(schema_confidences), 2),
                "max": round(max(schema_confidences), 2)
            }
    
    confidence_metrics = {
        "average": round(sum(confidence_values) / len(confidence_values), 2),
        "median": round(sorted(confidence_values)[len(confidence_values) // 2], 2),
        "by_schema": confidence_by_schema
    }
    
    return {
        "generated_at": datetime.datetime.now().isoformat(),
        "total_documents": len(documents),
        "schemas_used": schemas_used,
        "field_coverage": field_coverage,
        "confidence_metrics": confidence_metrics,
        "recent_classifications": documents[:5],
        "document_list": documents
    }

@api_bp.route('/reports', methods=['GET'])
def get_reports():
    return jsonify(generate_mock_data())

@api_bp.route('/reports/<schema_id>', methods=['GET'])
def get_schema_report(schema_id):
    mock_data = generate_mock_data()
    
    # Filter documents by schema_id
    documents = [doc for doc in mock_data["document_list"] if doc["schema_id"] == schema_id]
    
    if not documents:
        return jsonify({"error": f"No documents found for schema {schema_id}"}), 404
    
    schema_report = {
        "generated_at": mock_data["generated_at"],
        "schema_id": schema_id,
        "schema_title": documents[0]["schema_title"],
        "total_documents": len(documents),
        "field_coverage": {schema_id: mock_data["field_coverage"].get(schema_id, {})},
        "confidence_metrics": {
            "average": round(sum(doc["confidence"] for doc in documents) / len(documents), 2),
            "median": round(sorted([doc["confidence"] for doc in documents])[len(documents) // 2], 2)
        },
        "document_list": documents
    }
    
    return jsonify(schema_report)
