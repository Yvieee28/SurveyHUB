from app import db
from datetime import datetime
import secrets


class Survey(db.Model):
    __tablename__ = 'surveys'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    objective = db.Column(db.Text)
    target_audience = db.Column(db.String(200))
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, published, closed, archived
    public_token = db.Column(db.String(20), unique=True, nullable=True)
    form_password = db.Column(db.String(100), nullable=True, default=None)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    blocks = db.relationship('Block', backref='survey', lazy=True, cascade='all, delete-orphan')
    responses = db.relationship('Response', backref='survey', lazy=True)

    def generate_token(self):
        self.public_token = secrets.token_urlsafe(10)

    def __repr__(self):
        return f'<Survey {self.title}>'


class Block(db.Model):
    __tablename__ = 'blocks'

    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    questions = db.relationship('Question', backref='block', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Block {self.title}>'


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False, default='multiple_choice')
    required = db.Column(db.Boolean, nullable=False, default=True)
    position = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    choices = db.relationship('Choice', backref='question', lazy=True, cascade='all, delete-orphan')
    answers = db.relationship('Answer', backref='question', lazy=True)

    def __repr__(self):
        return f'<Question {self.text[:50]}>'


class Choice(db.Model):
    __tablename__ = 'choices'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    choice_text = db.Column(db.String(200), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Choice {self.choice_text}>'