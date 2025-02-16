from flask import Blueprint, jsonify, request
from models import Group, Word, StudySession, db
from sqlalchemy import desc

bp = Blueprint('groups', __name__)

@bp.route('/api/groups')
def list_groups():
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'name')
    order = request.args.get('order', 'asc')
    
    query = Group.query
    
    if sort_by in ['name', 'words_count']:
        if order == 'desc':
            query = query.order_by(desc(getattr(Group, sort_by)))
        else:
            query = query.order_by(getattr(Group, sort_by))
            
    paginated = query.paginate(page=page, per_page=100)
    
    return jsonify([{
        'id': group.id,
        'name': group.name,
        'words_count': group.words_count
    } for group in paginated.items])

@bp.route('/api/groups/<int:id>')
def get_group(id):
    group = Group.query.get_or_404(id)
    return jsonify({
        'id': group.id,
        'name': group.name,
        'words_count': group.words_count
    })

@bp.route('/api/groups/<int:id>/words')
def get_group_words(id):
    group = Group.query.get_or_404(id)
    return jsonify([{
        'id': word.id,
        'hangul': word.hangul,
        'romanization': word.romanization,
        'english': word.english,
        'type': word.type,
        'example': {
            'korean': word.example_korean,
            'english': word.example_english
        }
    } for word in group.words])

@bp.route('/api/groups/<int:id>/study_sessions')
def get_group_sessions(id):
    group = Group.query.get_or_404(id)
    return jsonify([{
        'id': session.id,
        'group_id': session.group_id,
        'created_at': session.created_at.isoformat(),
        'study_activity_id': session.study_activity_id
    } for session in group.study_sessions])
