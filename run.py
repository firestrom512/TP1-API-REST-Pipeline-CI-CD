"""Point d'entrée pour démarrer le serveur (python run.py)."""

from src.app import app

if __name__ == "__main__":
    app.run(debug=True)
