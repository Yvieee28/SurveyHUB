"""
CCI SurveyHUB - Database Seed Script
-------------------------------------
Seeds a moderate, realistic dataset for development and testing.
Run this once after the database is created (db.create_all()).

Usage:
    python seed.py
"""

import random
from datetime import datetime, timedelta

from app import create_app, db
from app.models.user import User
from app.models.survey import Survey, Block, Question, Choice
from app.models.response import Company, Response, Answer
from app.models.anomaly import Anomaly
from werkzeug.security import generate_password_hash

app = create_app()


# ──────────────────────────────────────────────────────────
# Helper data pools
# ──────────────────────────────────────────────────────────

COMPANY_PREFIXES = [
    'Nexus', 'Aether', 'Veridian', 'Oceanic', 'Quantum', 'Apex',
    'Meridian', 'Pioneer', 'Summit', 'Horizon', 'Atlas', 'Vertex',
    'Catalyst', 'Pinnacle', 'Sterling', 'Beacon', 'Orbit', 'Zenith',
    'Cascade', 'Phoenix', 'Crescent', 'Vector', 'Alpha', 'Delta'
]
COMPANY_SUFFIXES = [
    'Logistix', 'Tech', 'Group', 'Bio', 'Financials', 'Industries',
    'Solutions', 'Partners', 'Holdings', 'Dynamics', 'Systems',
    'Ventures', 'Capital', 'Networks', 'Consulting', 'Digital'
]

SURVEY_TITLES = [
    'Annual Commerce Index 2025',
    'Infrastructure Needs Analysis',
    'Quarterly Business Outlook Q3',
    'Maritime Trade Survey',
    'Workforce Training Needs 2025',
    'Regional Export Confidence Index',
    'Member Satisfaction Survey Q3',
    'Digital Transformation Readiness',
    'SME Growth Tracker 2025',
    'Sustainability Practices Survey',
]

STATUS_POOL = ['draft', 'published', 'published', 'published', 'closed', 'archived']

ANOMALY_TYPES = [
    ('email', 'invalid_format'),
    ('siret', 'too_short'),
    ('phone', 'missing_value'),
    ('email', 'missing_value'),
    ('siret', 'duplicate'),
]


def random_date_within(days_back):
    return datetime.utcnow() - timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )


def generate_siret():
    return ''.join(str(random.randint(0, 9)) for _ in range(14))


# ──────────────────────────────────────────────────────────
# Seed logic
# ──────────────────────────────────────────────────────────

with app.app_context():

    if User.query.first():
        print("Database already seeded. Skipping.")
        exit()

    # ---- USERS -------------------------------------------------
    print("Seeding users...")
    u1 = User(
        name='Jean Dupont', email='jean.dupont@cci.fr',
        password_hash=generate_password_hash('admin123'),
        role='admin', active=True
    )
    u2 = User(
        name='Marie Curie', email='marie.curie@cci.fr',
        password_hash=generate_password_hash('user123'),
        role='user', active=True
    )
    u3 = User(
        name='Paul Martin', email='paul.martin@cci.fr',
        password_hash=generate_password_hash('user123'),
        role='user', active=False
    )
    db.session.add_all([u1, u2, u3])
    db.session.commit()
    print(f"  {User.query.count()} users created.")

    # ---- COMPANIES (50) -----------------------------------------
    print("Seeding companies...")
    companies = []
    used_sirets = set()

    # Keep the 4 original "designed" companies first — they carry
    # the specific data-quality scenarios documented in Day 2.
    designed_companies = [
        Company(company_name='ABC Conseil', siret='12345678901234',
                email='contact@abc.fr', phone='0612345678'),
        Company(company_name='Martin Services', siret='9876543210',
                email='martinservices.fr', phone='061234'),
        Company(company_name='Alpha Digital', siret='12345678901234',
                email='alpha@digital.fr', phone='0687654321'),
        Company(company_name='Delta Formation', siret='56781234567890',
                email=None, phone=None),
    ]
    for c in designed_companies:
        companies.append(c)
        db.session.add(c)
        used_sirets.add(c.siret)

    # Fill the rest with random but valid companies (up to 50 total)
    while len(companies) < 50:
        name = f"{random.choice(COMPANY_PREFIXES)} {random.choice(COMPANY_SUFFIXES)}"
        siret = generate_siret()
        if siret in used_sirets:
            continue
        used_sirets.add(siret)
        company = Company(
            company_name=name,
            siret=siret,
            email=f"contact@{name.lower().replace(' ', '')}.com",
            phone=f"06{random.randint(10000000, 99999999)}",
            created_at=random_date_within(180)
        )
        companies.append(company)
        db.session.add(company)

    db.session.commit()
    print(f"  {len(companies)} companies created.")

    # ---- SURVEYS (10) ---------------------------------------------
    print("Seeding surveys...")
    surveys = []

    # Keep the original designed survey as survey #1
    s1 = Survey(
        title='Besoins Numériques 2025',
        description='Enquête sur la transformation digitale',
        objective='Identifier les besoins IT',
        target_audience='PME de Douala',
        status='published',
        public_token='a3f9bc12de',
        form_password='CCI2025',
        created_by=u1.id
    )
    db.session.add(s1)
    db.session.commit()
    surveys.append(s1)

    for title in SURVEY_TITLES:
        status = random.choice(STATUS_POOL)
        survey = Survey(
            title=title,
            description='Quarterly assessment for regional business intelligence.',
            objective='Track economic and operational indicators across member businesses.',
            target_audience='CCI member businesses',
            status=status,
            created_by=random.choice([u1.id, u2.id]),
            created_at=random_date_within(365)
        )
        if status == 'published':
            survey.generate_token()
        db.session.add(survey)
        surveys.append(survey)

    db.session.commit()
    published_surveys = [s for s in surveys if s.status == 'published']
    print(f"  {len(surveys)} surveys created ({len(published_surveys)} published).")

    # ---- BLOCKS / QUESTIONS / CHOICES ------------------------------
    print("Seeding blocks, questions and choices for survey #1...")
    b1 = Block(survey_id=s1.id, title='Informations Générales', position=1)
    b2 = Block(survey_id=s1.id, title='Besoins Actuels', position=2)
    b3 = Block(survey_id=s1.id, title='Satisfaction', position=3)
    db.session.add_all([b1, b2, b3])
    db.session.commit()

    q1 = Question(block_id=b1.id, text="Quel est votre secteur d'activité ?",
                  question_type='multiple_choice', required=True, position=1)
    q2 = Question(block_id=b1.id, text="Combien d'employés avez-vous ?",
                  question_type='multiple_choice', required=True, position=2)
    q3 = Question(block_id=b2.id, text="Quel est votre principal besoin numérique ?",
                  question_type='multiple_choice', required=True, position=1)
    q4 = Question(block_id=b3.id, text="Êtes-vous satisfait des services CCI ?",
                  question_type='multiple_choice', required=False, position=1)
    db.session.add_all([q1, q2, q3, q4])
    db.session.commit()

    db.session.add_all([
        Choice(question_id=q1.id, choice_text='Commerce', position=1),
        Choice(question_id=q1.id, choice_text='Industrie', position=2),
        Choice(question_id=q1.id, choice_text='Services', position=3),
        Choice(question_id=q2.id, choice_text='1-10 employés', position=1),
        Choice(question_id=q2.id, choice_text='11-50 employés', position=2),
        Choice(question_id=q2.id, choice_text='51-200 employés', position=3),
        Choice(question_id=q3.id, choice_text='Digitalisation', position=1),
        Choice(question_id=q3.id, choice_text='Cybersécurité', position=2),
        Choice(question_id=q3.id, choice_text='Formation numérique', position=3),
        Choice(question_id=q4.id, choice_text='Très satisfait', position=1),
        Choice(question_id=q4.id, choice_text='Satisfait', position=2),
        Choice(question_id=q4.id, choice_text='Insatisfait', position=3),
    ])
    db.session.commit()

    # Give a couple of the random surveys a minimal block/question too,
    # so results pages have more than one survey with content.
    for survey in random.sample(published_surveys, min(3, len(published_surveys))):
        if survey.id == s1.id:
            continue
        block = Block(survey_id=survey.id, title='Informations Générales', position=1)
        db.session.add(block)
        db.session.commit()
        question = Question(block_id=block.id, text="Quel est votre secteur d'activité ?",
                             question_type='multiple_choice', required=True, position=1)
        db.session.add(question)
        db.session.commit()
        for idx, text in enumerate(['Commerce', 'Industrie', 'Services', 'Logistique']):
            db.session.add(Choice(question_id=question.id, choice_text=text, position=idx + 1))
    db.session.commit()
    print("  Blocks, questions and choices seeded.")

    # ---- RESPONSES (50) ---------------------------------------------
    print("Seeding responses...")
    responses = []

    # Keep the 4 originally designed responses (tied to the 4 designed companies)
    designed_responses = [
        Response(survey_id=s1.id, company_id=designed_companies[0].id,
                 submitted_at=datetime(2025, 6, 4, 14, 0), completion_status='complete'),
        Response(survey_id=s1.id, company_id=designed_companies[1].id,
                 submitted_at=datetime(2025, 6, 4, 15, 0), completion_status='incomplete'),
        Response(survey_id=s1.id, company_id=designed_companies[2].id,
                 submitted_at=datetime(2025, 6, 4, 16, 0), completion_status='complete'),
        Response(survey_id=s1.id, company_id=designed_companies[3].id,
                 submitted_at=datetime(2025, 6, 5, 9, 0), completion_status='incomplete'),
    ]
    for r in designed_responses:
        db.session.add(r)
    db.session.commit()
    responses.extend(designed_responses)

    # Fill up to 50 total with random responses across published surveys
    while len(responses) < 50:
        survey = random.choice(published_surveys)
        company = random.choice(companies)
        status = random.choices(['complete', 'incomplete'], weights=[75, 25])[0]
        response = Response(
            survey_id=survey.id,
            company_id=company.id,
            submitted_at=random_date_within(30),
            completion_status=status
        )
        db.session.add(response)
        responses.append(response)

    db.session.commit()
    incomplete_count = sum(1 for r in responses if r.completion_status == 'incomplete')
    print(f"  {len(responses)} responses created ({incomplete_count} incomplete).")

    # ---- ANSWERS (tied to the 4 designed responses) ------------------
    print("Seeding answers...")
    db.session.add_all([
        Answer(response_id=designed_responses[0].id, question_id=q1.id, choice_id=3),  # Services
        Answer(response_id=designed_responses[0].id, question_id=q2.id, choice_id=4),  # 1-10 employés
        Answer(response_id=designed_responses[0].id, question_id=q3.id, choice_id=7),  # Digitalisation
        Answer(response_id=designed_responses[0].id, question_id=q4.id, choice_id=10), # Très satisfait
        Answer(response_id=designed_responses[1].id, question_id=q1.id, choice_id=1),  # Commerce
        Answer(response_id=designed_responses[2].id, question_id=q1.id, choice_id=2),  # Industrie
        Answer(response_id=designed_responses[2].id, question_id=q2.id, choice_id=5),  # 11-50 employés
        Answer(response_id=designed_responses[2].id, question_id=q3.id, choice_id=8),  # Cybersécurité
    ])
    db.session.commit()
    print(f"  {Answer.query.count()} answers created.")

    # ---- ANOMALIES (matching designed scenarios + a few extra) -------
    print("Seeding anomalies...")
    db.session.add_all([
        Anomaly(response_id=designed_responses[1].id, company_id=designed_companies[1].id,
                field_name='email', issue_type='invalid_format', status='open'),
        Anomaly(response_id=designed_responses[1].id, company_id=designed_companies[1].id,
                field_name='siret', issue_type='too_short', status='open'),
        Anomaly(response_id=designed_responses[2].id, company_id=designed_companies[2].id,
                field_name='siret', issue_type='duplicate', status='open'),
        Anomaly(response_id=designed_responses[3].id, company_id=designed_companies[3].id,
                field_name='phone', issue_type='missing_value', status='resolved',
                resolved_at=datetime(2025, 6, 6, 10, 0), resolved_by=u1.id),
        Anomaly(response_id=designed_responses[3].id, company_id=designed_companies[3].id,
                field_name='email', issue_type='missing_value', status='open'),
    ])

    # A handful of extra random anomalies pulled from the random responses,
    # so the anomalies page and dashboard counts feel populated (~15-20 total).
    random_pool = [r for r in responses if r not in designed_responses]
    sample_size = min(15, len(random_pool))
    for response in random.sample(random_pool, sample_size):
        field_name, issue_type = random.choice(ANOMALY_TYPES)
        status = random.choices(['open', 'resolved'], weights=[70, 30])[0]
        anomaly = Anomaly(
            response_id=response.id,
            company_id=response.company_id,
            field_name=field_name,
            issue_type=issue_type,
            status=status,
            resolved_at=random_date_within(10) if status == 'resolved' else None,
            resolved_by=u1.id if status == 'resolved' else None
        )
        db.session.add(anomaly)

    db.session.commit()
    print(f"  {Anomaly.query.count()} anomalies created.")

    # ---- SUMMARY -------------------------------------------------
    print("\nDatabase seeded successfully.")
    print("-" * 40)
    print(f"Users:      {User.query.count()}")
    print(f"Surveys:    {Survey.query.count()} ({len(published_surveys)} published)")
    print(f"Blocks:     {Block.query.count()}")
    print(f"Questions:  {Question.query.count()}")
    print(f"Choices:    {Choice.query.count()}")
    print(f"Companies:  {Company.query.count()}")
    print(f"Responses:  {Response.query.count()} ({incomplete_count} incomplete)")
    print(f"Answers:    {Answer.query.count()}")
    print(f"Anomalies:  {Anomaly.query.count()}")
    print("-" * 40)