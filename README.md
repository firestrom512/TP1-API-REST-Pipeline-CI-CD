# TP1 — API REST + Pipeline CI/CD

API Flask pour gérer un annuaire d'étudiants, avec stockage en mémoire, validations,
33 tests automatisés, lint Ruff et CI GitHub Actions (Python 3.11, 3.12, 3.13).

## Démarrage rapide (Windows / PowerShell)

**Sans commandes :** double-cliquez `DEMARRER-WINDOWS.bat` pour installer les dépendances
et lancer le serveur, ou `VERIFIER-WINDOWS.bat` pour lancer Ruff et pytest.


```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python run.py
```

Si PowerShell bloque l'activation, utilisez directement
`.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt`, puis
`.\.venv\Scripts\python.exe run.py`.

L'API est disponible sur `http://127.0.0.1:5000`.

## Tester et vérifier le code

```powershell
python -m pytest -q
ruff check .
```

## Les 7 endpoints

| Méthode | Route | Description |
| --- | --- | --- |
| GET | `/students` | Liste de tous les étudiants (200) |
| GET | `/students/<id>` | Étudiant (200), absent (404), ID invalide (400) |
| POST | `/students` | Création (201), invalidité (400), email déjà utilisé (409) |
| PUT | `/students/<id>` | Remplacement (200), validations, 404/400/409 |
| DELETE | `/students/<id>` | Suppression (200) ou absence (404) |
| GET | `/students/stats` | Nombre, moyenne, répartition, meilleur étudiant (200) |
| GET | `/students/search?q=ahmed` | Recherche prénom/nom (200), q absent (400) |

### Exemple de création

Utilisez PowerShell dans une **deuxième fenêtre** pendant que le serveur tourne :

```powershell
$body = @{
  firstName = "Fatou"
  lastName = "Ndiaye"
  email = "fatou@example.com"
  grade = 18
  field = "informatique"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://127.0.0.1:5000/students -Method Post -ContentType 'application/json' -Body $body
```

### Règles du modèle

- `id` : entier auto-incrémenté, unique.
- `firstName`, `lastName` : chaînes d'au moins 2 caractères.
- `email` : format email et unicité (insensible à la casse).
- `grade` : nombre de 0 à 20.
- `field` : `informatique`, `mathématiques`, `physique`, `chimie`.
- 5 étudiants préchargés ; `reset_data()` restaure le jeu initial.

## Pipeline GitHub Actions

Le pipeline est défini dans `.github/workflows/ci.yml`. Il se déclenche pour chaque
push et pull request vers `main` et suit les étapes : **Checkout → Setup Python →
Install → Lint → Test** pour trois versions de Python.

Pour obtenir un pipeline **vert**, pousser le dépôt sur GitHub et consulter l'onglet
**Actions**. Les tests doivent passer et Ruff ne doit détecter aucune erreur.

## Démonstration Red → Green (à faire sur GitHub)

1. Faire confirmer un pipeline **vert** et conserver une capture d'écran.
2. Modifier temporairement dans `src/app.py`, dans la fonction `list_students`,
   `return jsonify(data.students), 200` en `return jsonify(data.students), 201`.
3. Effectuer un commit `test: introduire un bug intentionnel pour démontrer le CI`,
   puis pousser : le test `test_list_students_returns_200_and_json_array` doit échouer.
4. Conserver la capture du pipeline **rouge**.
5. Restaurer le code `200`, puis effectuer un commit
   `fix: corriger le bug intentionnel` et pousser.
6. Vérifier le retour au **vert** et conserver une capture.

Ces captures **doivent provenir d'exécutions réelles de GitHub Actions** : elles
ne sont pas incluses dans l'archive car aucun pipeline GitHub n'a été exécuté
à partir de cette archive.

## Commits conventionnels suggérés

```text
chore: initialiser le projet Python Flask
feat(data): ajouter le modèle étudiant et les données initiales
feat(api): ajouter les routes GET, POST, PUT et DELETE
feat(api): ajouter les routes stats et search
test(api): ajouter les tests automatisés
chore(lint): configurer Ruff
ci: ajouter le pipeline GitHub Actions
```

## Structure

```text
TP1-API-REST-CI-CD/
├── .github/workflows/ci.yml
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── data.py
│   └── validation.py
├── tests/
│   ├── conftest.py
│   └── test_students.py
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── run.py
├── DEMARRER-WINDOWS.bat
├── VERIFIER-WINDOWS.bat
└── README.md
```
