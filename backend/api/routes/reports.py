from flask import Blueprint, jsonify
from api.services.document_service import DocumentService
from api.services.report_service import ReportService

# Initialize blueprint and services
reports_bp = Blueprint('reports', __name__)
document_service = DocumentService()
report_service = ReportService(document_service)

@reports_bp.route('/reports', methods=['GET'])
def get_reports():
    """
    Get full report data.
    
    :return: JSON response with report data
    """
    return jsonify(report_service.get_report())

@reports_bp.route('/reports/<schema_id>', methods=['GET'])
def get_schema_report(schema_id):
    """
    Get report data for a specific schema.
    
    :param schema_id: Schema identifier
    :return: JSON response with schema-specific report data
    """
    report = report_service.get_report(schema_id)
    
    if report is None:
        return jsonify({"error": f"No documents found for schema {schema_id}"}), 404
    
    return jsonify(report)