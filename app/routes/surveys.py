from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, session, send_file
from flask_login import login_required, current_user
from flask_babel import _
from app import db
from app.models.survey import Survey, Block, Question, Choice
from app.models.response import Response, Answer
from app.utils.import_helper import (
    is_survey_importable, get_survey_questions, generate_import_template,
    validate_import_file, commit_import, generate_rejected_report
)

surveys = Blueprint('surveys', __name__)

@surveys.route('/surveys')
@login_required
def survey_list():
    # Get filter and pagination params
    status_filter = request.args.get('status', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = 5
    
    # Build base query
    query = Survey.query.order_by(Survey.created_at.desc())
    
    # Apply status filter if provided and valid
    valid_statuses = ['draft', 'published', 'closed', 'archived']
    if status_filter and status_filter in valid_statuses:
        query = query.filter_by(status=status_filter)
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    survey_items = pagination.items
    total_pages = pagination.pages
    
    # Compute response counts for each survey
    surveys_with_counts = []
    for survey in survey_items:
        response_count = Response.query.filter_by(survey_id=survey.id).count()
        surveys_with_counts.append({
            'survey': survey,
            'response_count': response_count
        })
    
    return render_template(
        'surveys.html',
        surveys=surveys_with_counts,
        page=page,
        total_pages=total_pages,
        total_surveys=pagination.total,
        current_status=status_filter,
        valid_statuses=valid_statuses
    )

@surveys.route('/surveys/create')
@login_required
def create_survey():
    """Create a draft survey and redirect to the builder."""
    survey = Survey(
        title=_('Untitled Survey'),
        description='',
        objective='',
        target_audience='',
        status='draft',
        created_by=current_user.id
    )
    db.session.add(survey)
    db.session.commit()
    flash(_('Survey created. You can now build it.'), 'success')
    return redirect(url_for('surveys.survey_builder', id=survey.id))

@surveys.route('/surveys/<int:id>/builder')
@login_required
def survey_builder(id):
    """Render the survey builder page."""
    survey = Survey.query.get_or_404(id)
    return render_template('survey_builder.html', survey=survey)

@surveys.route('/surveys/<int:id>/update', methods=['POST'])
@login_required
def update_survey(id):
    """Update survey settings from the builder."""
    survey = Survey.query.get_or_404(id)
    survey.title = request.form.get('title', survey.title).strip()
    survey.description = request.form.get('description', survey.description).strip()
    survey.objective = request.form.get('objective', survey.objective).strip()
    survey.target_audience = request.form.get('target_audience', survey.target_audience).strip()
    survey.status = request.form.get('status', survey.status).strip()
    survey.form_password = request.form.get('form_password', '').strip() or None
    db.session.commit()
    flash(_('Survey settings saved.'), 'success')
    return redirect(url_for('surveys.survey_builder', id=survey.id))

@surveys.route('/surveys/<int:id>/blocks/add', methods=['POST'])
@login_required
def add_block(id):
    """Add a new block to the survey."""
    survey = Survey.query.get_or_404(id)
    title = request.form.get('title', '').strip()
    if not title:
        flash(_('Block title is required.'), 'danger')
        return redirect(url_for('surveys.survey_builder', id=survey.id))
    
    position = Block.query.filter_by(survey_id=survey.id).count() + 1
    block = Block(
        survey_id=survey.id,
        title=title,
        position=position
    )
    db.session.add(block)
    db.session.commit()
    flash(_('Block added.'), 'success')
    return redirect(url_for('surveys.survey_builder', id=survey.id))

@surveys.route('/blocks/<int:id>/questions/add', methods=['POST'])
@login_required
def add_question(id):
    """Add a new multiple-choice question to the block."""
    block = Block.query.get_or_404(id)
    text = request.form.get('text', '').strip()
    if not text:
        flash(_('Question text is required.'), 'danger')
        return redirect(url_for('surveys.survey_builder', id=block.survey_id))
    
    position = Question.query.filter_by(block_id=block.id).count() + 1
    question = Question(
        block_id=block.id,
        text=text,
        question_type='multiple_choice',
        required=True,
        position=position
    )
    db.session.add(question)
    db.session.commit()
    flash(_('Question added.'), 'success')
    return redirect(url_for('surveys.survey_builder', id=block.survey_id))

@surveys.route('/questions/<int:id>/choices/add', methods=['POST'])
@login_required
def add_choice(id):
    """Add a new choice to the question."""
    question = Question.query.get_or_404(id)
    choice_text = request.form.get('choice_text', '').strip()
    if not choice_text:
        flash(_('Choice text is required.'), 'danger')
        return redirect(url_for('surveys.survey_builder', id=question.block.survey_id))
    
    position = Choice.query.filter_by(question_id=question.id).count() + 1
    choice = Choice(
        question_id=question.id,
        choice_text=choice_text,
        position=position
    )
    db.session.add(choice)
    db.session.commit()
    flash(_('Choice added.'), 'success')
    return redirect(url_for('surveys.survey_builder', id=question.block.survey_id))

@surveys.route('/surveys/<int:id>/delete', methods=['POST'])
@login_required
def delete_survey(id):
    survey = Survey.query.get_or_404(id)
    
    # Check if survey has responses
    response_count = Response.query.filter_by(survey_id=survey.id).count()
    if response_count > 0:
        flash(_('Cannot delete survey with existing responses.'), 'danger')
        return redirect(url_for('surveys.survey_list'))
    
    db.session.delete(survey)
    db.session.commit()
    flash(_('Survey deleted successfully.'), 'success')
    return redirect(url_for('surveys.survey_list'))

@surveys.route('/surveys/<int:id>/preview')
@login_required
def preview_survey(id):
    """Render the survey preview page (read-only)."""
    survey = Survey.query.get_or_404(id)
    return render_template('preview.html', survey=survey)

@surveys.route('/surveys/<int:id>/publish', methods=['POST'])
@login_required
def publish_survey(id):
    """Publish the survey and generate a public token."""
    survey = Survey.query.get_or_404(id)
    
    if survey.status == 'published':
        flash(_('Survey is already published.'), 'info')
        return redirect(url_for('surveys.survey_builder', id=survey.id))
    
    survey.status = 'published'
    survey.generate_token()
    db.session.commit()
    
    public_url = url_for('responses.public_survey', token=survey.public_token, _external=True)
    flash(_('Survey published successfully! Public link: %(url)s', url=public_url), 'success')
    return redirect(url_for('surveys.survey_builder', id=survey.id))

@surveys.route('/surveys/<int:id>/edit')
@login_required
def edit_survey(id):
    return redirect(url_for('surveys.survey_builder', id=id))

@surveys.route('/surveys/<int:id>/results')
@login_required
def survey_results(id):
    """Display survey results with charts."""
    survey = Survey.query.get_or_404(id)
    
    # Get all responses for this survey
    responses = Response.query.filter_by(survey_id=survey.id).all()
    total_responses = len(responses)
    
    # Calculate completion rate
    complete_responses = sum(1 for r in responses if r.completion_status == 'complete')
    completion_rate = round((complete_responses / total_responses) * 100, 1) if total_responses > 0 else 0
    
    # Build results data per question
    question_results = []
    
    for block in survey.blocks:
        for question in block.questions:
            # Count answers per choice
            choice_data = []
            for choice in question.choices:
                count = Answer.query.filter_by(
                    question_id=question.id,
                    choice_id=choice.id
                ).count()
                choice_data.append({
                    'text': choice.choice_text,
                    'count': count,
                    'percentage': round((count / total_responses) * 100, 1) if total_responses > 0 else 0
                })
            
            question_results.append({
                'question': question,
                'choice_data': choice_data,
                'labels': [c['text'] for c in choice_data],
                'counts': [c['count'] for c in choice_data]
            })
    
    return render_template(
        'results.html',
        survey=survey,
        total_responses=total_responses,
        complete_responses=complete_responses,
        completion_rate=completion_rate,
        question_results=question_results,
        is_importable=is_survey_importable(survey)[0]
    )


@surveys.route('/surveys/<int:id>/import/template')
@login_required
def import_template(id):
    """Download Excel import template for the survey."""
    survey = Survey.query.get_or_404(id)
    importable, error_msg = is_survey_importable(survey)
    
    if not importable:
        flash(error_msg, 'warning')
        return redirect(url_for('surveys.survey_results', id=survey.id))
    
    output, filename = generate_import_template(survey)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


@surveys.route('/surveys/<int:id>/import')
@login_required
def import_upload(id):
    """Show the upload form for importing responses."""
    survey = Survey.query.get_or_404(id)
    importable, error_msg = is_survey_importable(survey)
    
    return render_template(
        'import_upload.html',
        survey=survey,
        importable=importable,
        error_msg=error_msg
    )


@surveys.route('/surveys/<int:id>/import', methods=['POST'])
@login_required
def import_validate(id):
    """Validate uploaded Excel file and show preview."""
    survey = Survey.query.get_or_404(id)
    importable, error_msg = is_survey_importable(survey)
    
    if not importable:
        flash(error_msg, 'warning')
        return redirect(url_for('surveys.survey_results', id=survey.id))
    
    if 'file' not in request.files:
        flash(_('No file uploaded.'), 'danger')
        return redirect(url_for('surveys.import_upload', id=survey.id))
    
    file = request.files['file']
    if not file.filename:
        flash(_('No file selected.'), 'danger')
        return redirect(url_for('surveys.import_upload', id=survey.id))
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        flash(_('Please upload an Excel file (.xlsx or .xls).'), 'danger')
        return redirect(url_for('surveys.import_upload', id=survey.id))
    
    # Validate the file
    result = validate_import_file(survey, file)
    
    if 'error' in result:
        flash(result['error'], 'danger')
        return redirect(url_for('surveys.import_upload', id=survey.id))
    
    # Store results in session for preview
    session['import_preview'] = {
        'survey_id': survey.id,
        'valid': result['valid'],
        'rejected': result['rejected'],
        'total': result['total']
    }
    
    return render_template(
        'import_preview.html',
        survey=survey,
        valid_rows=result['valid'],
        rejected_rows=result['rejected'],
        total_rows=result['total']
    )


@surveys.route('/surveys/<int:id>/import/confirm', methods=['POST'])
@login_required
def import_confirm(id):
    """Commit validated rows to database."""
    survey = Survey.query.get_or_404(id)
    
    preview = session.get('import_preview')
    if not preview or preview.get('survey_id') != survey.id:
        flash(_('No import data found. Please upload a file first.'), 'warning')
        return redirect(url_for('surveys.import_upload', id=survey.id))
    
    valid_rows = preview.get('valid', [])
    if not valid_rows:
        flash(_('No valid rows to import.'), 'warning')
        session.pop('import_preview', None)
        return redirect(url_for('surveys.survey_results', id=survey.id))
    
    imported_count = commit_import(survey, valid_rows)
    session.pop('import_preview', None)
    
    flash(_('Import completed successfully. %(count)d responses imported.', count=imported_count), 'success')
    return redirect(url_for('surveys.survey_results', id=survey.id))


@surveys.route('/surveys/<int:id>/import/rejected')
@login_required
def import_rejected(id):
    """Download rejected rows as CSV."""
    survey = Survey.query.get_or_404(id)
    
    preview = session.get('import_preview')
    if not preview or preview.get('survey_id') != survey.id:
        flash(_('No import data found.'), 'warning')
        return redirect(url_for('surveys.survey_results', id=survey.id))
    
    rejected_rows = preview.get('rejected', [])
    if not rejected_rows:
        flash(_('No rejected rows to download.'), 'info')
        return redirect(url_for('surveys.survey_results', id=survey.id))
    
    output, filename = generate_rejected_report(rejected_rows)
    if output:
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    
    flash(_('No rejected rows to download.'), 'info')
    return redirect(url_for('surveys.survey_results', id=survey.id))


@surveys.route('/surveys/<int:id>/import/cancel')
@login_required
def import_cancel(id):
    """Cancel import and clear session data."""
    session.pop('import_preview', None)
    flash(_('Import cancelled.'), 'info')
    return redirect(url_for('surveys.survey_results', id=id))
