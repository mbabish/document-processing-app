from flask import Blueprint, jsonify, request
from api.services.schema_service import SchemaService

# Initialize blueprint and service
schemas_bp = Blueprint('schemas', __name__)
schema_service = SchemaService()

@schemas_bp.route('/schemas', methods=['GET'])
def get_schemas():
    """
    Get list of available schemas
    
    Returns:
        JSON response with list of schemas
    """
    schemas = schema_service.get_schemas()
    return jsonify(schemas)

@schemas_bp.route('/schemas/<schema_id>', methods=['GET'])
def get_schema(schema_id):
    """
    Get a specific schema by ID
    
    Args:
        schema_id: Schema identifier
        
    Returns:
        JSON response with schema or error
    """
    schema = schema_service.get_schema(schema_id)
    if schema:
        return jsonify(schema)
    return jsonify({"error": f"Schema {schema_id} not found"}), 404

@schemas_bp.route('/schemas', methods=['POST'])
def add_schema():
    """
    Add a new schema
    
    Returns:
        JSON response indicating success or error
    """
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    schema_id = data.get('id')
    schema = data.get('schema')
    
    if not schema_id or not schema:
        return jsonify({"error": "ID and schema are required"}), 400
    
    success, error = schema_service.add_schema(schema_id, schema)
    if success:
        return jsonify({"message": f"Schema {schema_id} added successfully"}), 201
    return jsonify({"error": error}), 400

@schemas_bp.route('/schemas/<schema_id>', methods=['PUT'])
def update_schema(schema_id):
    """
    Update an existing schema
    
    Args:
        schema_id: Schema identifier
        
    Returns:
        JSON response indicating success or error
    """
    schema = request.json
    if not schema:
        return jsonify({"error": "No schema provided"}), 400
    
    success, error = schema_service.update_schema(schema_id, schema)
    if success:
        return jsonify({"message": f"Schema {schema_id} updated successfully"})
    return jsonify({"error": error}), 400

@schemas_bp.route('/schemas/<schema_id>', methods=['DELETE'])
def delete_schema(schema_id):
    """
    Delete a schema
    
    Args:
        schema_id: Schema identifier
        
    Returns:
        JSON response indicating success or error
    """
    success, error = schema_service.delete_schema(schema_id)
    if success:
        return jsonify({"message": f"Schema {schema_id} deleted successfully"})
    return jsonify({"error": error}), 404

@schemas_bp.route('/validate/<schema_id>', methods=['POST'])
def validate_document(schema_id):
    """
    Validate a document against a schema
    
    Args:
        schema_id: Schema identifier
        
    Returns:
        JSON response with validation result
    """
    document = request.json
    if not document:
        return jsonify({"error": "No document provided"}), 400
    
    is_valid, error = schema_service.validate_document(schema_id, document)
    return jsonify({
        "valid": is_valid,
        "schema_id": schema_id,
        "error": error
    })