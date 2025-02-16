from flask import Blueprint, jsonify, request
from models import Word, db
from sqlalchemy import desc

bp = Blueprint('words', __name__)

@bp.route('/words')
def list_words():
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'hangul')
    order = request.args.get('order', 'asc')
    
    query = Word.query
    
    if sort_by in ['hangul', 'romanization', 'english', 'type']:
        if order == 'desc':
            query = query.order_by(desc(getattr(Word, sort_by)))
        else:
            query = query.order_by(getattr(Word, sort_by))
            
    paginated = query.paginate(page=page, per_page=100, error_out=False)
    
    if not paginated.items:
        return jsonify([])
    
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
    } for word in paginated.items])

@bp.route('/words/<int:id>')
def get_word(id):
    word = Word.query.get_or_404(id)
    return jsonify({
        'id': word.id,
        'hangul': word.hangul,
        'romanization': word.romanization,
        'english': word.english,
        'type': word.type,
        'example': {
            'korean': word.example_korean,
            'english': word.example_english
        }
    })
