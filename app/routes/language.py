from flask import Blueprint, session, redirect, request
from flask_babel import refresh

language = Blueprint('language', __name__)

@language.route('/language/toggle', methods=['POST'])
def toggle_language():
    current = session.get('language', 'fr')
    session['language'] = 'en' if current == 'fr' else 'fr'
    refresh()
    return redirect(request.referrer or '/')
