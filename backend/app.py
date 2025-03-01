from flask import Flask
from flask_cors import CORS
from api.routes import api_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def health_check():
    return {"status": "ok", "message": "Document Processing API is running"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
