from flask import Blueprint, jsonify, request
from api.utils.file_utils import allowed_file, save_uploaded_file
from api.services.document_service import DocumentService
from config import Config

# Initialize blueprint and services
upload_bp = Blueprint('upload', __name__)
document_service = DocumentService()

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload and processing.
    
    :return: JSON response with upload and processing results
    """
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    # If user does not select file, browser also submits an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check if file is allowed
    if file and allowed_file(file.filename, Config.ALLOWED_EXTENSIONS):
        try:
            # Save the file
            filepath = save_uploaded_file(file, Config.UPLOAD_FOLDER)
            
            # Process the document
            document = document_service.process_document(file.filename, filepath)
            
            return jsonify({
                'success': True,
                'message': f'File uploaded and processed as {document["schema_title"]}',
                'document': document
            }), 201
        
        except Exception as e:
            return jsonify({
                'error': f'File upload and processing failed: {str(e)}'
            }), 500
        
    return jsonify({'error': 'File type not allowed'}), 400