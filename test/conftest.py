import os
import sys
import pytest
import json
import tempfile
import shutil

# Ajout du répertoire parent au path pour l'importation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session", autouse=True)
def backup_data_files():
    """Sauvegarde et restaure les fichiers de données pour les tests"""
    # Créer des copies temporaires des fichiers de données
    with tempfile.NamedTemporaryFile(delete=False) as clubs_backup:
        with open('clubs.json', 'r') as clubs_file:
            clubs_backup.write(clubs_file.read().encode())
    
    with tempfile.NamedTemporaryFile(delete=False) as competitions_backup:
        with open('competitions.json', 'r') as competitions_file:
            competitions_backup.write(competitions_file.read().encode())
    
    # Exécuter les tests
    yield
    
    # Restaurer les fichiers originaux
    shutil.copy2(clubs_backup.name, 'clubs.json')
    shutil.copy2(competitions_backup.name, 'competitions.json')
    
    # Nettoyer
    os.unlink(clubs_backup.name)
    os.unlink(competitions_backup.name)