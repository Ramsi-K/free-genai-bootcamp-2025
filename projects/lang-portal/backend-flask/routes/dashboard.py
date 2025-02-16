from flask import Blueprint, jsonify
from models import StudySession, WordReviewItem, db
from sqlalchemy import func

bp = Blueprint('dashboard', __name__)

@bp.route('/api/dashboard/last_study_session')
def last_study_session():
    session = StudySession.query.order_by(StudySession.created_at.desc()).first()
    if not session:
        return jsonify(None)
        
    return jsonify({
        'id': session.id,
        'group_id': session.group_id,
        'created_at': session.created_at.isoformat(),
        'study_activity_id': session.study_activity_id
    })

@bp.route('/api/dashboard/study_progress')
def study_progress():
    correct_count = WordReviewItem.query.filter_by(correct=True).count()
    wrong_count = WordReviewItem.query.filter_by(correct=False).count()
    
    return jsonify({
        'correct_count': correct_count,
        'wrong_count': wrong_count,
        'total_reviews': correct_count + wrong_count
    })

@bp.route('/api/dashboard/quick-stats')
def quick_stats():
    total_words = WordReviewItem.query.count()
    total_sessions = StudySession.query.count()
    
    return jsonify({
        'total_words_reviewed': total_words,
        'total_study_sessions': total_sessions
    })
