from flask import Blueprint, jsonify, request, current_app
import datetime
import random
import os
import uuid

api_bp = Blueprint('api', __name__)

# Define upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    # If user does not select file, browser also submits an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        original_filename = file.filename
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save the file
        file.save(filepath)
        
        # Auto-detect document type (in a real app, this would use ML/AI)
        # For now, we'll randomly choose a document type
        available_schemas = ["invoice", "receipt", "contract"]
        schema_id = random.choice(available_schemas)
        schema_title = schema_id.capitalize()
        
        # Generate a random classification ID
        classification_id = f"doc-{uuid.uuid4()}"
        
        # In a real application, you would process the document here
        # For now, we'll simulate processing with random confidence
        
        document = {
            "classification_id": classification_id,
            "filename": original_filename,
            "schema_id": schema_id,
            "schema_title": schema_title,
            "processed_at": datetime.datetime.now().isoformat(),
            "confidence": round(random.uniform(0.7, 0.99), 2),
            "fields_count": random.randint(5, 15),
            "filepath": filepath  # You might not want to expose this in production
        }
        
        return jsonify({
            'success': True,
            'message': f'File uploaded and processed as {schema_title}',
            'document': document
        }), 201
        
    return jsonify({'error': 'File type not allowed'}), 400

# Mock data for demonstration purposes
def generate_mock_data():
    schema_ids = ["invoice", "receipt", "contract"]
    schema_titles = {"invoice": "Invoice", "receipt": "Receipt", "contract": "Contract"}
    
    documents = []
    for i in range(20):
        schema_id = random.choice(schema_ids)
        documents.append({
            "classification_id": f"doc-{i+1}",
            "filename": f"document_{i+1}.pdf",
            "schema_id": schema_id,
            "schema_title": schema_titles[schema_id],
            "processed_at": (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))).isoformat(),
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
    
    return {
        "generated_at": datetime.datetime.now().isoformat(),
        "total_documents": len(documents),
        "schemas_used": schemas_used,
        "field_coverage": field_coverage,
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
        "document_list": documents
    }
    
    return jsonify(schema_report)