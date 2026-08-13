from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, session
from datetime import datetime
from flask_babel import _
from app import db
from app.models.survey import Survey
from app.models.response import Company, Response, Answer
from app.models.anomaly import Anomaly
from app.utils.validation import (
    validate_email, validate_siret, validate_phone,
    validate_required_fields, detect_duplicate_siret
)

responses = Blueprint('responses', __name__)


@responses.route('/survey/<token>')
def public_survey(token):
    survey = Survey.query.filter_by(public_token=token, status='published').first()
    if not survey:
        abort(404)
    if survey.form_password and not session.get(f'survey_{survey.id}_authenticated'):
        return render_template('form_password.html', survey=survey)
    return render_template('public_survey.html', survey=survey)


@responses.route('/survey/<token>/password', methods=['POST'])
def survey_password(token):
    survey = Survey.query.filter_by(public_token=token, status='published').first_or_404()
    if request.form.get('password') == survey.form_password:
        session[f'survey_{survey.id}_authenticated'] = True
        return redirect(url_for('responses.public_survey', token=token))
    return render_template('form_password.html', survey=survey, error=_('Incorrect password. Please try again.'))


@responses.route('/survey/<token>/submit', methods=['POST'])
def submit_survey(token):
    survey = Survey.query.filter_by(public_token=token, status='published').first_or_404()

    # 1. Extract form data
    company_name = request.form.get('company_name', '').strip()
    siret = request.form.get('siret', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()

    # 2. Run validations
    email_valid, email_error = validate_email(email)
    siret_valid, siret_error = validate_siret(siret)
    phone_valid, phone_error = validate_phone(phone)
    required_valid, required_errors = validate_required_fields(company_name, siret)

    # 3. Create or retrieve company
    company = Company.query.filter_by(siret=siret).first()
    if not company:
        company = Company(
            company_name=company_name,
            siret=siret,
            email=email,
            phone=phone
        )
        db.session.add(company)
        db.session.flush()
    else:
        company.company_name = company_name
        company.email = email
        company.phone = phone

    # 4. Create response
    response = Response(
        survey_id=survey.id,
        company_id=company.id,
        completion_status='incomplete',
        submitted_at=datetime.utcnow()
    )
    db.session.add(response)
    db.session.flush()

    # 5. Process answers
    required_question_ids = []
    answered_question_ids = []

    for block in survey.blocks:
        for question in block.questions:
            if question.required:
                required_question_ids.append(question.id)

            choice_id = request.form.get(f'question_{question.id}')
            if choice_id:
                answer = Answer(
                    response_id=response.id,
                    question_id=question.id,
                    choice_id=int(choice_id)
                )
                db.session.add(answer)
                answered_question_ids.append(question.id)

    # 6. Create anomalies for failed validations
    anomalies = []

    # Required field failures
    for field_name, message in required_errors.items():
        anomalies.append(Anomaly(
            response_id=response.id,
            company_id=company.id,
            field_name=field_name,
            issue_type='missing_value',
            status='open'
        ))

    # Format failures (only if value was provided)
    if not email_valid and email:
        anomalies.append(Anomaly(
            response_id=response.id,
            company_id=company.id,
            field_name='email',
            issue_type='invalid_format',
            status='open'
        ))

    if not siret_valid and siret:
        anomalies.append(Anomaly(
            response_id=response.id,
            company_id=company.id,
            field_name='siret',
            issue_type='invalid_format',
            status='open'
        ))

    if not phone_valid and phone:
        anomalies.append(Anomaly(
            response_id=response.id,
            company_id=company.id,
            field_name='phone',
            issue_type='invalid_format',
            status='open'
        ))

    # Duplicate SIRET check
    is_duplicate, existing = detect_duplicate_siret(siret, exclude_company_id=company.id)
    if is_duplicate:
        anomalies.append(Anomaly(
            response_id=response.id,
            company_id=company.id,
            field_name='siret',
            issue_type='duplicate',
            status='open'
        ))

    # Save all anomalies
    for anomaly in anomalies:
        db.session.add(anomaly)

    # 7. Determine completion status
    response.completion_status = 'incomplete' if anomalies else 'complete'

    db.session.commit()
    flash(_('Your response has been submitted successfully.'), 'success')
    return redirect(url_for('responses.thank_you', token=token))


@responses.route('/survey/<token>/thank-you')
def thank_you(token):
    survey = Survey.query.filter_by(public_token=token).first_or_404()
    return render_template('thank_you.html', survey=survey)
