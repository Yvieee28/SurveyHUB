import pandas as pd
from io import BytesIO
from flask_babel import _
from openpyxl.styles import Font
from app import db
from app.models.response import Response, Answer, Company
from app.models.survey import Survey, Question, Choice
from app.models.anomaly import Anomaly
from app.models.user import User


def export_responses_csv(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    responses = Response.query.filter_by(survey_id=survey_id).all()
    
    questions = []
    for block in survey.blocks:
        for question in block.questions:
            questions.append(question)
    
    rows = []
    for response in responses:
        company = Company.query.get(response.company_id)
        row = {
            _('Company Name'): company.company_name if company else '',
            _('SIRET'): company.siret if company else '',
            _('Email'): company.email if company else '',
            _('Phone'): company.phone if company else '',
            _('Submitted At'): response.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if response.submitted_at else '',
            _('Status'): response.completion_status
        }
        
        for question in questions:
            answer = Answer.query.filter_by(response_id=response.id, question_id=question.id).first()
            if answer and answer.choice_id:
                choice = Choice.query.get(answer.choice_id)
                row[question.text] = choice.choice_text if choice else ''
            else:
                row[question.text] = ''
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    
    filename = f"{survey.title.replace(' ', '_')}_responses.csv"
    return output, filename


def export_responses_excel(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    responses = Response.query.filter_by(survey_id=survey_id).all()
    
    questions = []
    for block in survey.blocks:
        for question in block.questions:
            questions.append(question)
    
    rows = []
    for response in responses:
        company = Company.query.get(response.company_id)
        row = {
            _('Company Name'): company.company_name if company else '',
            _('SIRET'): company.siret if company else '',
            _('Email'): company.email if company else '',
            _('Phone'): company.phone if company else '',
            _('Submitted At'): response.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if response.submitted_at else '',
            _('Status'): response.completion_status
        }
        
        for question in questions:
            answer = Answer.query.filter_by(response_id=response.id, question_id=question.id).first()
            if answer and answer.choice_id:
                choice = Choice.query.get(answer.choice_id)
                row[question.text] = choice.choice_text if choice else ''
            else:
                row[question.text] = ''
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=_('Responses'))
        workbook = writer.book
        worksheet = writer.sheets[_('Responses')]
        
        bold_font = Font(bold=True)
        for cell in worksheet[1]:
            cell.font = bold_font
        
        worksheet.auto_filter.ref = worksheet.dimensions
    
    output.seek(0)
    filename = f"{survey.title.replace(' ', '_')}_responses.xlsx"
    return output, filename


def export_anomalies_csv():
    anomalies = Anomaly.query.all()
    
    rows = []
    for anomaly in anomalies:
        company = Company.query.get(anomaly.company_id)
        resolved_by_user = User.query.get(anomaly.resolved_by) if anomaly.resolved_by else None
        
        row = {
            _('Company Name'): company.company_name if company else '',
            _('Field'): anomaly.field_name,
            _('Issue Type'): anomaly.issue_type,
            _('Status'): anomaly.status,
            _('Detected At'): anomaly.created_at.strftime('%Y-%m-%d %H:%M:%S') if anomaly.created_at else '',
            _('Resolved At'): anomaly.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if anomaly.resolved_at else '',
            _('Resolved By'): resolved_by_user.name if resolved_by_user else ''
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    
    filename = _("anomalies_report.csv")
    return output, filename
