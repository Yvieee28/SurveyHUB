from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel

db = SQLAlchemy()
login_manager = LoginManager()
babel = Babel()

def get_locale():
    if 'language' in session:
        return session['language']
    return 'fr'

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'cci-surveyhub-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///surveyhub.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['BABEL_DEFAULT_LOCALE'] = 'fr'

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    babel.init_app(app, locale_selector=get_locale)

    from app.routes.auth import auth
    from app.routes.dashboard import dashboard
    from app.routes.surveys import surveys
    from app.routes.responses import responses
    from app.routes.exports import exports
    from app.routes.assistant import assistant
    from app.routes.language import language

    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(surveys)
    app.register_blueprint(responses)
    app.register_blueprint(exports)
    app.register_blueprint(assistant)
    app.register_blueprint(language)

    with app.app_context():
        from app.models.user import User
        from app.models.survey import Survey, Block, Question, Choice
        from app.models.response import Company, Response, Answer
        from app.models.anomaly import Anomaly
        db.create_all()

    return app
