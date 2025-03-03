import os

class Config:
    # Upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = {'pdf'}

    # Ensure required folders exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Configure maximum file upload size (16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # CORS configuration
    CORS_ORIGINS = '*'  # In production, replace with specific origins
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_HEADERS = ['Content-Type', 'Authorization']