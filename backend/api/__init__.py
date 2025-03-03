from flask import Blueprint

# Import individual routes
from .routes.upload import upload_bp
from .routes.schemas import schemas_bp
from .routes.reports import reports_bp

def register_blueprints(app):
    """
    Register all blueprints with the Flask application.
    
    :param app: Flask application instance
    """
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(schemas_bp, url_prefix='/api')
    app.register_blueprint(reports_bp, url_prefix='/api')