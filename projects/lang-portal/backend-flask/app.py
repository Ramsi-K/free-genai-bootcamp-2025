from flask import Flask, jsonify
from models import db
from routes import words, groups, study_sessions, dashboard
import os

def create_app():
    app = Flask(__name__)
    
    # Ensure instance path exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
        
    # Configure SQLAlchemy
    app.config.update(
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'words.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # Initialize SQLAlchemy with the Flask app
    db.init_app(app)
    
    # Register blueprints with URL prefixes
    app.register_blueprint(words.bp, url_prefix='/api')
    app.register_blueprint(groups.bp, url_prefix='/api')
    app.register_blueprint(study_sessions.bp, url_prefix='/api')
    app.register_blueprint(dashboard.bp, url_prefix='/api')
    
    # Add root route
    @app.route('/')
    def index():
        return jsonify({
            'name': 'Korean Language Learning API',
            'version': '1.0',
            'description': 'API for managing Korean vocabulary and study sessions',
            'endpoints': {
                'words': {
                    'list': '/api/words',
                    'get': '/api/words/<id>',
                    'parameters': {
                        'page': 'Page number (default: 1)',
                        'sort_by': 'Sort field (hangul, romanization, english, type)',
                        'order': 'Sort order (asc, desc)'
                    }
                },
                'groups': {
                    'list': '/api/groups',
                    'get': '/api/groups/<id>',
                    'words': '/api/groups/<id>/words',
                    'study_sessions': '/api/groups/<id>/study_sessions'
                },
                'study_sessions': {
                    'list': '/api/study_sessions',
                    'create': '/api/study_sessions',
                    'review': '/api/study_sessions/<id>/words/<word_id>/review'
                },
                'dashboard': {
                    'last_session': '/api/dashboard/last_study_session',
                    'progress': '/api/dashboard/study_progress',
                    'stats': '/api/dashboard/quick-stats'
                }
            }
        })
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Resource not found'}), 404
        
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Invalid input', 'message': str(e)}), 400
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)