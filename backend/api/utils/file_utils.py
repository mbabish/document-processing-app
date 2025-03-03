import os
import uuid
from typing import Set
from werkzeug.datastructures import FileStorage

def allowed_file(filename: str, allowed_extensions: Set[str]) -> bool:
    """
    Check if file has an allowed extension
    
    Args:
        filename: Name of the file to check
        allowed_extensions: Set of allowed extensions
        
    Returns:
        True if file has an allowed extension, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file: FileStorage, upload_folder: str) -> str:
    """
    Save an uploaded file with a unique filename
    
    Args:
        file: FileStorage object to save
        upload_folder: Directory to save the file in
        
    Returns:
        Path to the saved file
    """
    # Ensure upload folder exists
    os.makedirs(upload_folder, exist_ok=True)
    
    # Generate a unique filename
    original_filename = file.filename
    unique_filename = f"{uuid.uuid4()}_{original_filename}"
    filepath = os.path.join(upload_folder, unique_filename)
    
    # Save the file
    file.save(filepath)
    
    return filepath