from flask import Blueprint, render_template, send_file, flash
from flask_login import login_required
from app.utils.export_helper import export_responses_csv, export_responses_excel, export_anomalies_csv

exports = Blueprint('exports', __name__)

@exports.route('/exports')
@login_required
def export_index():
    return render_template('exports.html')

@exports.route('/surveys/<int:id>/export/csv')
@login_required
def export_csv(id):
    output, filename = export_responses_csv(id)
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@exports.route('/surveys/<int:id>/export/excel')
@login_required
def export_excel(id):
    output, filename = export_responses_excel(id)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@exports.route('/exports/anomalies/csv')
@login_required
def export_anomalies():
    output, filename = export_anomalies_csv()
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )
