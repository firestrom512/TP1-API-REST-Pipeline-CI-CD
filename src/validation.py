"""Validation des données envoyées à l'API."""

import re

FIELDS = {"informatique", "mathématiques", "physique", "chimie"}
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
REQUIRED_FIELDS = ("firstName", "lastName", "email", "grade", "field")


def validate_student(payload, existing_students, exclude_id=None):
    """Retourner (données nettoyées, message d'erreur, code HTTP)."""
    if not isinstance(payload, dict):
        return None, "Un objet JSON est requis.", 400

    if any(field not in payload for field in REQUIRED_FIELDS):
        return None, "Tous les champs sont obligatoires.", 400

    first_name = payload["firstName"]
    last_name = payload["lastName"]
    email = payload["email"]
    grade = payload["grade"]
    field = payload["field"]

    for name, value in (("firstName", first_name), ("lastName", last_name)):
        if not isinstance(value, str) or len(value.strip()) < 2:
            return None, f"{name} doit contenir au moins 2 caractères.", 400

    if not isinstance(email, str) or not EMAIL_PATTERN.fullmatch(email.strip()):
        return None, "Format d'email invalide.", 400

    # En Python, bool est un sous-type de int : on l'exclut explicitement.
    if isinstance(grade, bool) or not isinstance(grade, (int, float)):
        return None, "La note doit être un nombre entre 0 et 20.", 400
    if not 0 <= grade <= 20:
        return None, "La note doit être comprise entre 0 et 20.", 400

    if not isinstance(field, str) or field not in FIELDS:
        return None, "Filière non autorisée.", 400

    email = email.strip()
    for student in existing_students:
        if student["id"] != exclude_id and student["email"].casefold() == email.casefold():
            return None, "Cet email est déjà utilisé.", 409

    clean_payload = {
        "firstName": first_name.strip(),
        "lastName": last_name.strip(),
        "email": email,
        "grade": grade,
        "field": field,
    }
    return clean_payload, None, None
