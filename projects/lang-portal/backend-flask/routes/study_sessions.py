from flask import Blueprint, jsonify, request
from models import StudySession, WordReviewItem, db
from datetime import datetime

bp = Blueprint('study_sessions', __name__)

@bp.route('/api/study_sessions')
def list_sessions():
    page = request.args.get('page', 1, type=int)
    sessions = StudySession.query.paginate(page=page, per_page=100)
    
    return jsonify([{
        'id': session.id,
        'group_id': session.group_id,
        'created_at': session.created_at.isoformat(),
        'study_activity_id': session.study_activity_id
    } for session in sessions.items])

@bp.route('/api/study_sessions', methods=['POST'])
def create_session():
    data = request.get_json()
    if 'group_id' not in data:
        return jsonify({'error': 'Invalid input', 'message': 'group_id is required'}), 400
        
    session = StudySession(group_id=data['group_id'])
    db.session.add(session)
    db.session.commit()
    
    return jsonify({
        'id': session.id,
        'group_id': session.group_id
    })

@bp.route('/api/study_sessions/<int:id>/words/<int:word_id>/review', methods=['POST'])
def review_word(id, word_id):
    data = request.get_json()
    if 'correct' not in data:
        return jsonify({'error': 'Invalid input', 'message': 'correct parameter is required'}), 400
        
    review = WordReviewItem(
        word_id=word_id,
        study_session_id=id,
        correct=data['correct']
    )
    db.session.add(review)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Review recorded.'})