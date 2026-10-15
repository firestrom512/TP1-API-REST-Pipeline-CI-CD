
"""Données en mémoire pour l'annuaire d'étudiants."""

from copy import deepcopy

ALLOWED_FIELDS = ("informatique", "mathématiques", "physique", "chimie")

INITIAL_STUDENTS = [
    {
        "id": 1,
        "firstName": "Ahmed",
        "lastName": "Diallo",
        "email": "ahmed@example.com",
        "grade": 16,
        "field": "informatique",
    },
    {
        "id": 2,
        "firstName": "Marie",
        "lastName": "Martin",
        "email": "Marie@example.com",
        "grade": 14,
        "field": "chimie",
    },
    {
        "id": 3,
        "firstName": "Ali",
        "lastName": "Traoré",
        "email": "Ali@example.com",
        "grade": 9,
        "field": "physique",
    },
    {
        "id": 4,
        "firstName": "Fatou",
        "lastName": "Koné",
        "email": "Fatou@example.com",
        "grade": 11,
        "field": "mathématiques",
    },
    {
        "id": 5,
        "firstName": "Jean",
        "lastName": "Dupont",
        "email": "Jean@example.com",
        "grade": 16,
        "field": "informatique",
    },
]

students = []
next_id = 1


def reset_students():
    """Restaure les étudiants initiaux et le prochain identifiant."""
    global students, next_id
    students = deepcopy(INITIAL_STUDENTS)
    next_id = max(student["id"] for student in students) + 1
