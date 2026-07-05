# CCI SurveyHUB

> Create. Collect. Verify. Analyse.

A web application designed for the Chamber of Commerce and Industry (CCI) to centralise 
the creation, distribution, collection and analysis of business surveys.

---

## Project Overview

CCI SurveyHUB was built to solve a real data management problem observed during an 
internship at the CCI. Survey responses were scattered across multiple Excel files, 
company records contained missing or invalid data, and analysis was slow and unreliable.

This application brings everything into one place:
- Create structured surveys with blocks and multiple-choice questions
- Share surveys with companies through a public link
- Automatically detect data quality issues on submission
- Visualise results through a simple dashboard
- Export clean data to CSV or Excel for Power BI reporting

---

## Stack

| Layer | Technology |
|-------|------------|
| Backend | Python Flask |
| Database | SQLite + Flask-SQLAlchemy |
| Authentication | Flask-Login + Werkzeug password hashing |
| Frontend | HTML, CSS, Bootstrap 5, JavaScript |
| Data Processing | Pandas |
| Charts | Chart.js |
| Exports | Pandas + OpenPyXL |
| AI Assistant | Google GenAI (Gemini) |
| Environment | python-dotenv |

---

## Project Structure

```
CCI-SurveyHUB/
├── app/
│   ├── __init__.py          # App factory, blueprint registration
│   ├── routes/
│   │   ├── auth.py          # Login and logout (Flask-Login)
│   │   ├── dashboard.py     # Main dashboard — real DB queries
│   │   ├── surveys.py       # Survey list, builder, blocks, questions, choices, publish, results
│   │   ├── responses.py     # Public response form with password gate (token-based access)
│   │   ├── exports.py       # CSV and Excel exports
│   │   ├── assistant.py     # AI assistant (Gemini-powered chat)
│   ├── utils/
│   │   ├── export_helper.py # Pandas + OpenPyXL export logic
│   │   ├── validation.py    # Email, SIRET, phone validators
│   ├── models/
│   │   ├── user.py          # Users table
│   │   ├── survey.py        # Surveys, blocks, questions, choices
│   │   ├── response.py      # Companies, responses, answers
│   │   ├── anomaly.py       # Anomalies table
│   ├── templates/
│   │   ├── base.html        # Base layout with sidebar, navbar, and AI chat widget
│   │   ├── login.html       # Login page
│   │   ├── dashboard.html   # Dashboard wired to real data
│   │   ├── surveys.html     # Survey list with filters and pagination
│   │   ├── survey_builder.html  # Survey builder — blocks, questions, choices
│   │   ├── preview.html     # Survey preview (real nested data)
│   │   ├── public_survey.html  # Public-facing response form
│   │   ├── form_password.html  # Password gate for protected surveys
│   │   ├── results.html     # Results and charts
│   │   ├── anomalies.html   # Anomalies management
│   │   ├── exports.html     # Export page
│   │   ├── thank_you.html   # Post-submission thank-you page
│   ├── static/
│   │   ├── css/
│   │   │   └── main.css
│   │   ├── js/
│   │   │   └── main.js
├── documentation/
│   ├── README.md
│   ├── user_guide.md
│   ├── installation.md
│   └── bug_tracking.md
├── instance/
│   └── surveyhub.db         # SQLite database (gitignored)
├── seed.py                  # Database seed script — dummy data
├── requirements.txt
├── run.py
└── .gitignore
```

---

## Features

### Authentication
- Login page with email and password
- Session management via Flask-Login
- All internal pages protected with `@login_required`
- Logout clears the session and redirects to login
- Active/inactive user accounts supported via `is_active` flag

### Survey Management
- Create surveys with title, description, objective and target audience
- Organise questions into blocks for better structure
- Add multiple-choice questions with predefined answer choices
- Add, edit and remove answer choices per question
- Preview survey with real nested data before publishing
- Generate unique public link on publish (`public_token`)
- Track survey status: Draft → Published → Closed → Archived
- Filter survey list by status (All / Published / Draft / Closed)
- Paginated survey list
- Delete protection — surveys with existing responses cannot be deleted

### Data Collection
- Public response form accessible without login via `/survey/<token>`
- Token-based access — only published surveys are reachable
- Companies fill in their information (name, SIRET, email, phone) 
  and answer questions
- Client-side required field validation on the public form
- Response persists company info, answers, and submission timestamp
- Optional password protection — respondents must enter a password before accessing the form

### Data Quality Control (Planned — Week 3)
Automatic validation will run on every submission:

| Field | Rule |
|-------|------|
| Email | Must contain valid format with @ |
| SIRET | Must be exactly 14 digits |
| Phone | Must be exactly 10 digits |
| Required fields | Cannot be empty |
| Duplicates | Detected by matching SIRET |

All issues will be logged to the anomalies table and visible on the anomalies page.

### Dashboard
- Total surveys created (real count from database)
- Published surveys count
- Total responses received
- Incomplete records count
- Potential duplicates count
- Latest responses feed (5 most recent)
- Response volume chart (Chart.js)

### Results and Analysis
- Response count per survey with summary cards (total, complete, completion rate)
- Answer distribution per question displayed in data tables
- Bar charts via Chart.js for each multiple-choice question
- Charts auto-generated from collected response data
- Charts render with responsive layout and clean styling

### Exports
- Survey responses exported as CSV or Excel
- Columns: Company Name, SIRET, Email, Phone, Submitted At, Status, plus one column per question
- Excel exports have bold header row and auto-filter (Power BI ready)
- Anomalies report exported as CSV
- Export buttons available on the Results page and Exports page

### Password Protection
- Optional password field on each survey
- Respondents must enter the password before accessing the public form
- Password gate shows a clean entry screen with error handling
- Password stored on the survey model — NULL means no protection

### AI Assistant
- Floating chat widget available on all internal pages
- Powered by Google Gemini (gemini-2.0-flash)
- System prompt scoped to CCI SurveyHUB guidance only
- Markdown-formatted responses with bullet points and bold text
- Requires authentication — only CCI staff can use it

---

## Database Schema

9 tables covering the full survey lifecycle:

| Table | Purpose |
|-------|---------|
| users | Internal CCI staff and admins |
| surveys | Survey metadata and status |
| blocks | Question groups inside a survey |
| questions | Individual survey questions |
| choices | Predefined answer options |
| companies | Business respondent information |
| responses | One completed or partial survey submission |
| answers | Selected choices per response |
| anomalies | Detected data quality issues |

### Schema Notes

- `surveys.public_token` stores the unique token used to build the 
  shareable public link, generated only when a survey is published
- `anomalies.company_id` allows direct querying of anomalies by 
  company without joining through responses
- `anomalies.resolved_at` and `resolved_by` provide an audit trail 
  for resolved data quality issues
- `answers.text_value` supports future open-ended question types 
  in addition to predefined choice selections
- `users.active` (note: not `is_active`) tracks whether a user 
  account is enabled — renamed from the original schema design 
  to avoid a naming conflict with Flask-Login's `UserMixin.is_active` 
  property

---

## Installation

See `documentation/installation.md` for full setup instructions.

Quick start:

```bash
git clone https://github.com/yourusername/CCI-SurveyHUB.git
cd CCI-SurveyHUB
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
python seed.py
```

Then open `http://127.0.0.1:5000` in your browser.

**Seeded test accounts:**

| Email | Password | Role |
|-------|----------|------|
| jean.dupont@cci.fr | admin123 | admin |
| marie.curie@cci.fr | user123 | user |

---

## Usage

See `documentation/user_guide.md` for full usage instructions.

---

## Development Roadmap

| Week | Focus | Status |
|------|-------|--------|
| Week 1 | Project setup, structure, database schema | ✅ Complete |
| Week 2 | Authentication, dashboard, survey builder, preview, publish | ✅ Complete |
| Week 3 | Public response collection, validation, anomalies | ✅ Complete |
| Week 4 | Results, charts, exports, password protection, AI assistant | ✅ Complete |

### Week 2 Summary

| Day | Focus | Outcome |
|-----|-------|---------|
| Day 6 | Authentication | Login/logout working with Flask-Login, routes protected |
| Day 7 | Dashboard | Real database queries replacing static dummy numbers |
| Day 8 | Survey List | Functional status filters, pagination, delete protection |
| Day 9 | Survey Builder | Create survey, add blocks, add questions, add choices — full CRUD |
| Day 10 | Preview + Publish | Real nested preview rendering, publish route with token generation, public survey page wired to database |

### Week 4 Summary

| Day | Focus | Outcome |
|-----|-------|---------|
| Day 14 | Results Page | Charts and data tables per question, summary cards, completion rate |
| Day 17 | Exports | CSV and Excel exports for responses and anomalies using Pandas + OpenPyXL |
| Day 18 | Password Protection | Optional survey password, password gate page, session-based access |
| Day 19 | AI Assistant | Gemini-powered chat widget with markdown rendering, scoped to app guidance |

---

## Team

| Person | Responsibility |
|--------|---------------|
| Person 1 | Web interface, Flask routes, templates, Bootstrap design |
| Person 2 | Database models, validation logic, exports, charts |

---

## Documentation

| File | Content |
|------|---------|
| README.md | Project overview and setup |
| user_guide.md | How to use the application |
| installation.md | Step by step technical setup |
| bug_tracking.md | Bugs encountered and fixes applied |

---

## Limitations (MVP)

This is a first version MVP. The following features are out of scope 
for this release:

- Conditional logic between questions
- Automatic email campaigns
- Advanced user role management
- Direct Power BI API connection
- Predictive analysis module
- Mobile application
- Open-ended text questions

---

## License

Internal project — CCI internship context.
Not intended for public distribution.

---

## Acknowledgements

Inspired by professional survey platforms such as Qualtrics.
Built as an internal MVP adapted to the specific needs of the CCI.