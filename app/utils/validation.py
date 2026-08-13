import re
from flask_babel import _
from app.models.response import Company


def validate_email(email):
    """Optional but format-checked. Returns (is_valid, error_message)."""
    if not email:
        return True, ""
    if re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return True, ""
    return False, _("Invalid email format")


def validate_siret(siret):
    """Required: exactly 14 digits."""
    if not siret:
        return False, _("SIRET is required")
    if not siret.isdigit():
        return False, _("SIRET must contain only digits")
    if len(siret) != 14:
        return False, _("SIRET must be exactly 14 digits (got %(num)d)", num=len(siret))
    return True, ""


def validate_phone(phone):
    """Optional but format-checked: 10 digits when provided."""
    if not phone:
        return True, ""
    digits_only = re.sub(r'\D', '', phone)
    if len(digits_only) != 10:
        return False, _("Phone must be 10 digits (got %(num)d)", num=len(digits_only))
    return True, ""


def validate_required_fields(company_name, siret):
    """Required fields: company_name and siret must not be empty."""
    errors = {}
    if not company_name or not company_name.strip():
        errors['company_name'] = _("Company name is required")
    if not siret or not siret.strip():
        errors['siret'] = _("SIRET is required")
    return len(errors) == 0, errors


def detect_duplicate_siret(siret, exclude_company_id=None):
    """Check if another company already has this SIRET."""
    query = Company.query.filter_by(siret=siret)
    if exclude_company_id:
        query = query.filter(Company.id != exclude_company_id)
    existing = query.first()
    if existing:
        return True, existing
    return False, None
