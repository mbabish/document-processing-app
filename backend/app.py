from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from api import register_blueprints
import traceback
import sys

def create_app(config_class=Config):
    """
    Create and configure the Flask application.
    
    :param config_class: Configuration class to use
    :return: Configured Flask application
    """
    # Create Flask app instance
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    register_blueprints(app)
    
    return app

# Create app instance for use with WSGI servers or development
app = create_app()

# Add a simple health check route
@app.route('/')
def health_check():
    """
    Simple health check endpoint.
    
    :return: JSON response indicating app is running
    """
    return {
        "status": "ok",
        "message": "Document Processing API is running"
    }

@app.errorhandler(Exception)
def handle_exception(e):
    """
    Global error handler to log full traceback
    """
    # Log the full traceback to stderr
    print("An error occurred:", file=sys.stderr)
    traceback.print_exc()
    
    # Prepare error response
    error_response = {
        "error": "Internal Server Error",
        "message": str(e),
        # Optional: include traceback in development
        "traceback": traceback.format_exc() if app.config['DEBUG'] else None
    }
    
    return jsonify(error_response), 500

# Allow running the app directly for development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)