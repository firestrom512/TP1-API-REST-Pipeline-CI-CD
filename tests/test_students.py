"""Tests automatisés de l'API REST (les 15 requis + cas limites)."""

from copy import deepcopy

from src.data import INITIAL_STUDENTS, students

VALID_STUDENT = {
    "firstName": "Fatou",
    "lastName": "Ndiaye",
    "email": "fatou.ndiaye@example.com",
    "grade": 18,
    "field": "informatique",
}


def test_list_students_returns_200_and_json_array(client):
    response = client.get("/students")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_list_students_returns_five_initial_students(client):
    response = client.get("/students")
    assert len(response.get_json()) == len(INITIAL_STUDENTS) == 5


def test_get_existing_student_returns_200(client):
    response = client.get("/students/1")
    assert response.status_code == 200
    assert response.get_json()["email"] == INITIAL_STUDENTS[0]["email"]


def test_get_unknown_student_returns_404(client):
    response = client.get("/students/999")
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_get_invalid_id_returns_400(client):
    response = client.get("/students/abc")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_post_valid_student_returns_201_and_id(client):
    response = client.post("/students", json=VALID_STUDENT)
    assert response.status_code == 201
    assert response.get_json()["id"] == 6
    assert response.get_json()["firstName"] == "Fatou"


def test_post_missing_required_field_returns_400(client):
    invalid = {key: value for key, value in VALID_STUDENT.items() if key != "email"}
    response = client.post("/students", json=invalid)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_post_grade_above_20_returns_400(client):
    invalid = {**VALID_STUDENT, "grade": 25}
    response = client.post("/students", json=invalid)
    assert response.status_code == 400


def test_post_duplicate_email_returns_409(client):
    invalid = {**VALID_STUDENT, "email": INITIAL_STUDENTS[0]["email"]}
    response = client.post("/students", json=invalid)
    assert response.status_code == 409
    assert "error" in response.get_json()


def test_put_valid_student_returns_200_and_updates(client):
    response = client.put("/students/1", json=VALID_STUDENT)
    assert response.status_code == 200
    assert response.get_json()["firstName"] == "Fatou"
    assert client.get("/students/1").get_json()["email"] == VALID_STUDENT["email"]


def test_put_unknown_id_returns_404(client):
    response = client.put("/students/999", json=VALID_STUDENT)
    assert response.status_code == 404


def test_delete_existing_student_returns_200(client):
    response = client.delete("/students/1")
    assert response.status_code == 200
    assert response.get_json()["id"] == 1
    assert client.get("/students/1").status_code == 404


def test_delete_unknown_student_returns_404(client):
    response = client.delete("/students/999")
    assert response.status_code == 404


def test_stats_returns_required_keys(client):
    response = client.get("/students/stats")
    payload = response.get_json()
    assert response.status_code == 200
    assert {"totalStudents", "averageGrade", "studentsByField", "bestStudent"} <= payload.keys()
    assert payload["totalStudents"] == 5
    assert payload["averageGrade"] == 15.6
    assert payload["bestStudent"]["id"] == 3


def test_search_returns_matching_students(client):
    response = client.get("/students/search?q=ahmed")
    assert response.status_code == 200
    assert [student["id"] for student in response.get_json()] == [2]


def test_search_is_case_insensitive(client):
    response = client.get("/students/search?q=AMINATA")
    assert response.status_code == 200
    assert response.get_json()[0]["id"] == 1


def test_search_without_query_returns_400(client):
    response = client.get("/students/search")
    assert response.status_code == 400


def test_search_with_blank_query_returns_400(client):
    response = client.get("/students/search?q=%20%20")
    assert response.status_code == 400


def test_post_invalid_email_returns_400(client):
    response = client.post("/students", json={**VALID_STUDENT, "email": "pas-un-email"})
    assert response.status_code == 400


def test_post_invalid_first_name_returns_400(client):
    response = client.post("/students", json={**VALID_STUDENT, "firstName": "F"})
    assert response.status_code == 400


def test_post_invalid_last_name_returns_400(client):
    response = client.post("/students", json={**VALID_STUDENT, "lastName": "N"})
    assert response.status_code == 400


def test_post_invalid_field_returns_400(client):
    response = client.post("/students", json={**VALID_STUDENT, "field": "histoire"})
    assert response.status_code == 400


def test_post_negative_grade_returns_400(client):
    response = client.post("/students", json={**VALID_STUDENT, "grade": -1})
    assert response.status_code == 400


def test_post_boolean_grade_returns_400(client):
    response = client.post("/students", json={**VALID_STUDENT, "grade": True})
    assert response.status_code == 400


def test_post_missing_json_returns_400(client):
    response = client.post("/students", data="not JSON", content_type="text/plain")
    assert response.status_code == 400


def test_post_duplicate_email_ignores_case(client):
    response = client.post(
        "/students", json={**VALID_STUDENT, "email": "AMINATA.DIALLO@EXAMPLE.COM"}
    )
    assert response.status_code == 409


def test_put_email_of_same_student_is_allowed(client):
    updated = {**VALID_STUDENT, "email": INITIAL_STUDENTS[0]["email"]}
    response = client.put("/students/1", json=updated)
    assert response.status_code == 200
    assert response.get_json()["id"] == 1


def test_put_duplicate_email_of_other_student_returns_409(client):
    updated = {**VALID_STUDENT, "email": INITIAL_STUDENTS[1]["email"]}
    response = client.put("/students/1", json=updated)
    assert response.status_code == 409


def test_put_invalid_payload_returns_400(client):
    response = client.put("/students/1", json={**VALID_STUDENT, "grade": 22})
    assert response.status_code == 400


def test_post_ids_are_auto_incremented_after_deletion(client):
    client.delete("/students/5")
    first = client.post("/students", json=VALID_STUDENT)
    second = client.post(
        "/students", json={**VALID_STUDENT, "email": "autre@example.com"}
    )
    assert (first.get_json()["id"], second.get_json()["id"]) == (6, 7)


def test_reset_prevents_test_data_leaks(client):
    assert len(students) == 5
    assert students == deepcopy(INITIAL_STUDENTS)


def test_delete_invalid_id_returns_400(client):
    response = client.delete("/students/non-numerique")
    assert response.status_code == 400


def test_stats_after_deleting_all_students(client):
    for student in deepcopy(INITIAL_STUDENTS):
        client.delete(f"/students/{student['id']}")
    response = client.get("/students/stats")
    assert response.status_code == 200
    assert response.get_json() == {
        "totalStudents": 0,
        "averageGrade": 0,
        "studentsByField": {},
        "bestStudent": None,
    }
