
"""15 tests automatisés pour l'API REST des étudiants."""

import pytest

from src import data
from src.app import app


# Préparation des tests

@pytest.fixture(autouse=True)
def reset_before_each_test():
    """Réinitialise les 5 étudiants avant chaque test."""
    data.reset_students()


@pytest.fixture
def client():
    """Crée un client HTTP Flask sans démarrer le serveur."""
    app.config["TESTING"] = True
    return app.test_client()


def nouvel_etudiant():
    """Données valides pour créer un étudiant."""
    return {
        "firstName": "Nina",
        "lastName": "Moreau",
        "email": "nina@example.com",
        "grade": 17,
        "field": "chimie",
    }


# TEST 1 : GET liste, code 200

def test_01_liste_status(client):
    response = client.get("/students")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


# TEST 2 : GET liste, 5 étudiants

def test_02_liste_cinq_etudiants(client):
    response = client.get("/students")
    students = response.get_json()

    assert response.status_code == 200
    assert len(students) == 5


# TEST 3 : GET étudiant avec ID valide

def test_03_get_etudiant_valide(client):
    response = client.get("/students/1")
    student = response.get_json()

    assert response.status_code == 200
    assert student["id"] == 1
    assert student["firstName"] == "Ahmed"


# TEST 4 : GET étudiant inexistant

def test_04_get_etudiant_inexistant(client):
    response = client.get("/students/999")

    assert response.status_code == 404
    assert "error" in response.get_json()


# TEST 5 : GET identifiant non numérique

def test_05_get_id_invalide(client):
    response = client.get("/students/abc")

    assert response.status_code == 400
    assert "error" in response.get_json()


# TEST 6 : POST données valides

def test_06_post_valide(client):
    response = client.post(
        "/students",
        json=nouvel_etudiant()
    )

    student = response.get_json()

    assert response.status_code == 201
    assert student["id"] == 6
    assert student["firstName"] == "Nina"


# TEST 7 : POST champ obligatoire absent

def test_07_post_sans_email(client):
    student = nouvel_etudiant()
    del student["email"]

    response = client.post("/students", json=student)

    assert response.status_code == 400
    assert "error" in response.get_json()


# TEST 8 : POST note invalide

def test_08_post_note_invalide(client):
    student = nouvel_etudiant()
    student["grade"] = 25

    response = client.post("/students", json=student)

    assert response.status_code == 400
    assert "error" in response.get_json()


# TEST 9 : POST email déjà utilisé

def test_09_post_email_doublon(client):
    student = nouvel_etudiant()
    student["email"] = "ahmed@example.com"

    response = client.post("/students", json=student)

    assert response.status_code == 409
    assert "error" in response.get_json()


# TEST 10 : PUT modification valide

def test_10_put_valide(client):
    student = {
        "firstName": "Ahmed",
        "lastName": "Diallo",
        "email": "ahmed@example.com",
        "grade": 18,
        "field": "mathématiques",
    }

    response = client.put("/students/1", json=student)
    result = response.get_json()

    assert response.status_code == 200
    assert result["grade"] == 18
    assert result["field"] == "mathématiques"

    verification = client.get("/students/1")
    assert verification.get_json()["grade"] == 18


# TEST 11 : PUT étudiant inexistant

def test_11_put_inexistant(client):
    response = client.put(
        "/students/999",
        json=nouvel_etudiant()
    )

    assert response.status_code == 404
    assert "error" in response.get_json()


# TEST 12 : DELETE étudiant existant

def test_12_delete_valide(client):
    response = client.delete("/students/1")

    assert response.status_code == 200
    assert response.get_json()["id"] == 1

    verification = client.get("/students/1")
    assert verification.status_code == 404


# TEST 13 : DELETE étudiant inexistant

def test_13_delete_inexistant(client):
    response = client.delete("/students/999")

    assert response.status_code == 404
    assert "error" in response.get_json()


# TEST 14 : GET statistiques

def test_14_statistiques(client):
    response = client.get("/students/stats")
    stats = response.get_json()

    assert response.status_code == 200

    assert "totalStudents" in stats
    assert "averageGrade" in stats
    assert "studentsByField" in stats
    assert "bestStudent" in stats

    assert stats["totalStudents"] == 5
    assert stats["averageGrade"] == 13.2
    assert stats["studentsByField"]["informatique"] == 2


# TEST 15 : GET recherche étudiant

def test_15_recherche(client):
    response = client.get("/students/search?q=ahmed")
    results = response.get_json()

    assert response.status_code == 200
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["firstName"] == "Ahmed"
