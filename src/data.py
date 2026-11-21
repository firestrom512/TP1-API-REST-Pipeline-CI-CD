"""Stockage en mémoire et jeu de données initial."""

from copy import deepcopy

INITIAL_STUDENTS = [
    {
        "id": 1,
        "firstName": "Aminata",
        "lastName": "Diallo",
        "email": "aminata.diallo@example.com",
        "grade": 17,
        "field": "informatique",
    },
    {
        "id": 2,
        "firstName": "Ahmed",
        "lastName": "Benali",
        "email": "ahmed.benali@example.com",
        "grade": 14,
        "field": "mathématiques",
    },
    {
        "id": 3,
        "firstName": "Clara",
        "lastName": "Martin",
        "email": "clara.martin@example.com",
        "grade": 19,
        "field": "physique",
    },
    {
        "id": 4,
        "firstName": "Moussa",
        "lastName": "Traoré",
        "email": "moussa.traore@example.com",
        "grade": 12,
        "field": "chimie",
    },
    {
        "id": 5,
        "firstName": "Lina",
        "lastName": "Moreau",
        "email": "lina.moreau@example.com",
        "grade": 16,
        "field": "informatique",
    },
]

students = []
next_id = 1


def reset_data():
    """Restaurer les cinq étudiants de départ et le prochain identifiant."""
    global next_id
    students.clear()
    students.extend(deepcopy(INITIAL_STUDENTS))
    next_id = max(item["id"] for item in students) + 1


def create_student(payload):
    """Ajouter un étudiant validé en lui attribuant un ID unique."""
    global next_id
    student = {"id": next_id, **payload}
    students.append(student)
    next_id += 1
    return student


reset_data()
