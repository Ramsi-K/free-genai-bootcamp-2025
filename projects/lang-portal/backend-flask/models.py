from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import JSON

# Create the SQLAlchemy instance locally
db = SQLAlchemy()

class Word(db.Model):
    __tablename__ = 'words'
    
    id = db.Column(db.Integer, primary_key=True)
    hangul = db.Column(db.String, nullable=False)
    romanization = db.Column(db.String, nullable=False)
    english = db.Column(JSON, nullable=False)
    type = db.Column(db.String, nullable=False)
    example_korean = db.Column(db.String)
    example_english = db.Column(db.String)
    
    groups = db.relationship('Group', secondary='words_groups', back_populates='words')
    reviews = db.relationship('WordReviewItem', back_populates='word')

class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    words_count = db.Column(db.Integer, default=0)
    
    words = db.relationship('Word', secondary='words_groups', back_populates='groups')
    study_sessions = db.relationship('StudySession', back_populates='group')

class WordsGroups(db.Model):
    __tablename__ = 'words_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)

class StudySession(db.Model):
    __tablename__ = 'study_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    study_activity_id = db.Column(db.Integer, db.ForeignKey('study_activities.id'))
    
    group = db.relationship('Group', back_populates='study_sessions')
    activity = db.relationship('StudyActivity', back_populates='sessions')
    reviews = db.relationship('WordReviewItem', back_populates='study_session')

class StudyActivity(db.Model):
    __tablename__ = 'study_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    thumbnail_url = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    sessions = db.relationship('StudySession', back_populates='activity')

class WordReviewItem(db.Model):
    __tablename__ = 'word_review_items'
    
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    study_session_id = db.Column(db.Integer, db.ForeignKey('study_sessions.id'), nullable=False)
    correct = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    word = db.relationship('Word', back_populates='reviews')
    study_session = db.relationship('StudySession', back_populates='reviews') 