from flask import Flask
from models import db
from routes import words, groups, study_sessions, dashboard

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/words.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy with the Flask app
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(words.bp)
    app.register_blueprint(groups.bp)
    app.register_blueprint(study_sessions.bp)
    app.register_blueprint(dashboard.bp)
    
    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Resource not found'}, 404
        
    @app.errorhandler(400)
    def bad_request(e):
        return {'error': 'Invalid input', 'message': str(e)}, 400
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)