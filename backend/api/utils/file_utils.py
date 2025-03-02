import os
import uuid

def allowed_file(filename, allowed_extensions):
    """
    Check if the filename has an allowed extension.
    
    :param filename: Name of the file to check
    :param allowed_extensions: Set of allowed file extensions
    :return: Boolean indicating if file is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_unique_filename(original_filename):
    """
    Generate a unique filename by prepending a UUID.
    
    :param original_filename: Original name of the file
    :return: Unique filename
    """
    return f"{uuid.uuid4()}_{original_filename}"

def save_uploaded_file(file, upload_folder):
    """
    Save an uploaded file to the specified folder.
    
    :param file: File object from the request
    :param upload_folder: Destination folder for the file
    :return: Full path to the saved file
    """
    unique_filename = generate_unique_filename(file.filename)
    filepath = os.path.join(upload_folder, unique_filename)
    file.save(filepath)
    return filepath