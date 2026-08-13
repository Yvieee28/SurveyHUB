from app import db
from datetime import datetime


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    siret = db.Column(db.String(20))
    email = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    responses = db.relationship('Response', backref='company', lazy=True)
    anomalies = db.relationship('Anomaly', backref='company', lazy=True)

    def __repr__(self):
        return f'<Company {self.company_name}>'


class Response(db.Model):
    __tablename__ = 'responses'

    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    completion_status = db.Column(db.String(20), nullable=False, default='incomplete')  # complete or incomplete
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    answers = db.relationship('Answer', backref='response', lazy=True, cascade='all, delete-orphan')
    anomalies = db.relationship('Anomaly', backref='response', lazy=True)

    def __repr__(self):
        return f'<Response {self.id} - Survey {self.survey_id}>'


class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('responses.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    choice_id = db.Column(db.Integer, db.ForeignKey('choices.id'), nullable=True)
    text_value = db.Column(db.Text, nullable=True)  # for future open-ended questions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Answer response={self.response_id} question={self.question_id}>'