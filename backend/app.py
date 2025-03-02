from flask import Flask, jsonify
from flask_cors import CORS
from api.routes import api_bp
import os

app = Flask(__name__)
# Enable CORS for all routes with more specific configuration
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configure maximum file upload size (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def health_check():
    return jsonify({"status": "ok", "message": "Document Processing API is running"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)