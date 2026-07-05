from app import db
from datetime import datetime


class Anomaly(db.Model):
    __tablename__ = 'anomalies'

    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('responses.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    field_name = db.Column(db.String(50), nullable=False)   # email, siret, phone etc
    issue_type = db.Column(db.String(50), nullable=False)   # invalid_format, too_short, duplicate, missing_value
    status = db.Column(db.String(20), nullable=False, default='open')  # open or resolved
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Anomaly {self.field_name} - {self.issue_type}>'