"""Routes REST de l'annuaire d'étudiants."""

import re
from collections import Counter

from flask import Flask, jsonify, request

from src import data
from src.validation import validate_student

app = Flask(__name__)


def error(message, status):
    """Construire une réponse JSON d'erreur."""
    return jsonify({"error": message}), status


def parse_student_id(raw_id):
    """Convertir l'ID ou lever ValueError s'il n'est pas valide."""
    if not re.fullmatch(r"[0-9]+", raw_id):
        raise ValueError("L'identifiant doit être un entier positif.")
    return int(raw_id)


def get_student(student_id):
    """Retrouver un étudiant dans le stockage en mémoire."""
    return next((item for item in data.students if item["id"] == student_id), None)


@app.get("/students")
def list_students():
    return jsonify(data.students), 201


# Les routes littérales doivent être déclarées avant /students/<student_id>.
@app.get("/students/stats")
def student_stats():
    students = data.students
    fields = Counter(student["field"] for student in students)
    best_student = max(students, key=lambda student: student["grade"], default=None)
    average = (
        round(sum(student["grade"] for student in students) / len(students), 2)
        if students
        else 0
    )
    return jsonify(
        {
            "totalStudents": len(students),
            "averageGrade": average,
            "studentsByField": dict(fields),
            "bestStudent": best_student,
        }
    ), 200


@app.get("/students/search")
def search_students():
    term = request.args.get("q", "").strip()
    if not term:
        return error("Le paramètre q est obligatoire.", 400)
    query = term.casefold()
    matches = [
        student
        for student in data.students
        if query in student["firstName"].casefold() or query in student["lastName"].casefold()
    ]
    return jsonify(matches), 200


@app.get("/students/<student_id>")
def read_student(student_id):
    try:
        parsed_id = parse_student_id(student_id)
    except ValueError as exc:
        return error(str(exc), 400)
    student = get_student(parsed_id)
    if student is None:
        return error("Étudiant introuvable.", 404)
    return jsonify(student), 200


@app.post("/students")
def add_student():
    payload, message, status = validate_student(request.get_json(silent=True), data.students)
    if message:
        return error(message, status)
    return jsonify(data.create_student(payload)), 201


@app.put("/students/<student_id>")
def update_student(student_id):
    try:
        parsed_id = parse_student_id(student_id)
    except ValueError as exc:
        return error(str(exc), 400)
    student = get_student(parsed_id)
    if student is None:
        return error("Étudiant introuvable.", 404)
    payload, message, status = validate_student(
        request.get_json(silent=True), data.students, exclude_id=parsed_id
    )
    if message:
        return error(message, status)
    student.update(payload)
    return jsonify(student), 200


@app.delete("/students/<student_id>")
def delete_student(student_id):
    try:
        parsed_id = parse_student_id(student_id)
    except ValueError as exc:
        return error(str(exc), 400)
    student = get_student(parsed_id)
    if student is None:
        return error("Étudiant introuvable.", 404)
    data.students.remove(student)
    return jsonify({"message": "Étudiant supprimé.", "id": parsed_id}), 200


if __name__ == "__main__":
    app.run(debug=True)
