from flask import Blueprint, request, jsonify
from flask_login import login_required
from flask_babel import _
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

assistant = Blueprint('assistant', __name__)

SYSTEM_PROMPT = _("""You are a helpful assistant inside CCI SurveyHUB, an internal survey management application for the Chamber of Commerce and Industry.

You help CCI staff navigate and use the application. You only answer questions about how to use CCI SurveyHUB. If asked anything unrelated, politely redirect to app-related questions.

The application has these main sections:
- Dashboard: shows total surveys, responses, anomalies and latest activity
- Surveys: create and manage surveys, add blocks and questions, preview and publish
- Anomalies: review data quality issues detected on form submission, mark them as resolved
- Exports: download response data as CSV or Excel for Power BI reporting

Common tasks you can help with:
- How to create a new survey: Click "Surveys" → "Create Survey" → fill settings → add blocks and questions → publish
- How to add blocks and questions: In survey builder, click "Add Block" then "Add Question" under each block
- How to publish a survey: In survey builder, click "Publish" button → copy public link
- How to set a password on a public form: In survey settings, fill "Response Password" field → save
- How to preview a survey: Click "Preview" button in survey builder
- How to view results and charts: From surveys list, click the chart icon → see charts and export options
- How to mark an anomaly as resolved: Go to Anomalies → click "Resolve" on any open anomaly
- How to export data: From results page, click "Export CSV" or "Export Excel" buttons

Keep responses concise and actionable. Use bullet points for steps.""")

@assistant.route('/assistant/ask', methods=['POST'])
@login_required
def ask_assistant():
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'error': _('Message is required')}), 400
    
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return jsonify({'error': _('API key not configured')}), 500
        
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=SYSTEM_PROMPT + '\n\nUser question: ' + message
        )
        
        return jsonify({'response': response.text})
    
    except Exception as e:
        return jsonify({'error': _('Assistant error: %(error)s', error=str(e))}), 500
