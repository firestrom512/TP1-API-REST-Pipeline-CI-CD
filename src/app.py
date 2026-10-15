
"""API REST Flask pour un annuaire d'étudiants."""

import math
import re

from flask import Flask, jsonify, request
from src import data

app = Flask(__name__)
data.reset_students()

REQUIRED_FIELDS = ("firstName", "lastName", "email", "grade", "field")

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def error(message, status):
    """Retourne une erreur au format JSON."""
    return jsonify({"error": message}), status


def parse_id(raw_id):
    """Lit un identifiant entier positif ; None si invalide."""
    if not raw_id.isdecimal() or int(raw_id) < 1:
        return None
    return int(raw_id)


def find_student(student_id):
    """Cherche un étudiant par son identifiant."""
    return next(
        (s for s in data.students if s["id"] == student_id),
        None
    )


def validate_student(payload, current_id=None):
    """Valide les données POST/PUT et l'unicité de l'email."""

    if not isinstance(payload, dict):
        return None, "Le corps doit être un objet JSON", 400

    if any(field not in payload for field in REQUIRED_FIELDS):
        return None, "Tous les champs sont obligatoires", 400

    first_name = payload["firstName"]
    last_name = payload["lastName"]
    email = payload["email"]
    grade = payload["grade"]
    field = payload["field"]

    if not isinstance(first_name, str) or len(first_name.strip()) < 2:
        return None, "firstName doit contenir au moins 2 caractères", 400

    if not isinstance(last_name, str) or len(last_name.strip()) < 2:
        return None, "lastName doit contenir au moins 2 caractères", 400

    if not isinstance(email, str) or not EMAIL_PATTERN.fullmatch(email.strip()):
        return None, "Format d'email invalide", 400

    if isinstance(grade, bool) or not isinstance(grade, (int, float)):
        return None, "La note doit être un nombre", 400

    if not math.isfinite(grade) or not 0 <= grade <= 20:
        return None, "La note doit être comprise entre 0 et 20", 400

    if not isinstance(field, str) or field not in data.ALLOWED_FIELDS:
        return None, "Filière non autorisée", 400

    normalized_email = email.strip().lower()

    for student in data.students:
        if student["email"].lower() == normalized_email:
            if student["id"] != current_id:
                return None, "Cet email existe déjà", 409

    cleaned = {
        "firstName": first_name.strip(),
        "lastName": last_name.strip(),
        "email": normalized_email,
        "grade": grade,
        "field": field,
    }

    return cleaned, None, None


@app.get("/students")
def list_students():
    """Renvoie la liste complète des étudiants."""
    return jsonify(data.students), 200


@app.get("/students/stats")
def stats():
    """Renvoie les indicateurs de l'annuaire."""

    total = len(data.students)

    average = (
        round(sum(s["grade"] for s in data.students) / total, 2)
        if total else 0
    )

    by_field = {
        field: sum(s["field"] == field for s in data.students)
        for field in data.ALLOWED_FIELDS
    }

    best = max(
        data.students,
        key=lambda s: s["grade"],
        default=None
    )

    return jsonify({
        "totalStudents": total,
        "averageGrade": average,
        "studentsByField": by_field,
        "bestStudent": best,
    }), 200


@app.get("/students/search")
def search_students():
    """Recherche par prénom ou nom, sans tenir compte de la casse."""

    query = request.args.get("q", "").strip()

    if not query:
        return error("Le paramètre q est obligatoire", 400)

    needle = query.casefold()

    matches = [
        s for s in data.students
        if needle in s["firstName"].casefold()
        or needle in s["lastName"].casefold()
    ]

    return jsonify(matches), 200


@app.get("/students/<student_id>")
def get_student(student_id):
    """Renvoie un étudiant identifié par son ID."""

    parsed_id = parse_id(student_id)

    if parsed_id is None:
        return error("Identifiant invalide", 400)

    student = find_student(parsed_id)

    if student is None:
        return error("Étudiant introuvable", 404)

    return jsonify(student), 200


@app.post("/students")
def create_student():
    """Crée un étudiant après validation."""

    cleaned, message, status = validate_student(
        request.get_json(silent=True)
    )

    if message:
        return error(message, status)

    student = {"id": data.next_id, **cleaned}

    data.students.append(student)
    data.next_id += 1

    return jsonify(student), 200 


@app.put("/students/<student_id>")
def update_student(student_id):
    """Remplace les informations d'un étudiant existant."""

    parsed_id = parse_id(student_id)

    if parsed_id is None:
        return error("Identifiant invalide", 400)

    student = find_student(parsed_id)

    if student is None:
        return error("Étudiant introuvable", 404)

    cleaned, message, status = validate_student(
        request.get_json(silent=True),
        current_id=parsed_id
    )

    if message:
        return error(message, status)

    student.update(cleaned)

    return jsonify(student), 200


@app.delete("/students/<student_id>")
def delete_student(student_id):
    """Supprime un étudiant et retourne une confirmation."""

    parsed_id = parse_id(student_id)

    if parsed_id is None:
        return error("Identifiant invalide", 400)

    student = find_student(parsed_id)

    if student is None:
        return error("Étudiant introuvable", 404)

    data.students.remove(student)

    return jsonify({
        "message": "Étudiant supprimé",
        "id": parsed_id
    }), 200
