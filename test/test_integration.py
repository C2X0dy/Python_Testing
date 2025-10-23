import os
import sys
import json
import pytest

# Ajout du répertoire parent au path pour l'importation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import du serveur Flask
import server

@pytest.fixture
def client():
    """Fixture pour créer un client de test"""
    server.app.config['TESTING'] = True
    with server.app.test_client() as client:
        yield client

def test_booking_workflow(client):
    """Test complet du workflow de réservation"""
    # 1. Charger les données initiales
    with open('competitions.json', 'r') as f:
        competitions_data = json.load(f)
        initial_places = int(competitions_data['competitions'][0]['numberOfPlaces'])
    
    with open('clubs.json', 'r') as f:
        clubs_data = json.load(f)
        initial_points = int(clubs_data['clubs'][0]['points'])
    
    try:
        # 2. Connexion (login)
        login_response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
        assert login_response.status_code == 200
        assert b'Welcome back!' in login_response.data
        
        # 3. Accéder à la page de réservation
        booking_page = client.get('/book/Spring Festival/Simply Lift')
        assert booking_page.status_code == 200
        assert b'Booking: Spring Festival' in booking_page.data
        
        # 4. Effectuer la réservation
        purchase_response = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Spring Festival',
            'places': '3'  # Réserver 3 places
        }, follow_redirects=True)
        
        assert purchase_response.status_code == 200
        assert b'Great! Booking complete!' in purchase_response.data
        
        # 5. Vérifier que les données ont été mises à jour
        with open('competitions.json', 'r') as f:
            competitions_data = json.load(f)
            updated_places = int(competitions_data['competitions'][0]['numberOfPlaces'])
            assert updated_places == initial_places - 3
        
        with open('clubs.json', 'r') as f:
            clubs_data = json.load(f)
            updated_points = int(clubs_data['clubs'][0]['points'])
            assert updated_points == initial_points - 9  # 3 places * 3 points = 9 points
        
        # 6. Se déconnecter
        logout_response = client.get('/logout', follow_redirects=True)
        assert logout_response.status_code == 200
        assert b'Secretary Login' in logout_response.data
        
    finally:
        # Restaurer les données originales
        with open('competitions.json', 'r+') as f:
            data = json.load(f)
            data['competitions'][0]['numberOfPlaces'] = str(initial_places)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
        
        with open('clubs.json', 'r+') as f:
            data = json.load(f)
            data['clubs'][0]['points'] = str(initial_points)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

def test_points_reflection_after_booking(client):
    """Test que les points sont correctement mis à jour sur le tableau public après réservation"""
    # 1. Connexion
    client.post('/showSummary', data={'email': 'john@simplylift.co'})
    
    # 2. Enregistrer les points initiaux
    points_initial = client.get('/points')
    
    # 3. Effectuer une réservation
    initial_points = 13  # Simply Lift commence avec 13 points
    
    try:
        client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Spring Festival',
            'places': '1'  # Réserver 1 place (3 points)
        }, follow_redirects=True)
        
        # 4. Vérifier les points mis à jour sur le tableau
        points_after = client.get('/points')
        
        # Vérifier que les points ont diminué de 3
        assert str(initial_points).encode() in points_initial.data
        assert str(initial_points - 3).encode() in points_after.data
    
    finally:
        # Restaurer les données originales
        with open('clubs.json', 'r+') as f:
            data = json.load(f)
            data['clubs'][0]['points'] = str(initial_points)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

def test_multiple_bookings_same_competition(client):
    """Test de réservations multiples pour la même compétition"""
    
    # IMPORTANT: Restaurer explicitement les valeurs initiales avant de commencer le test
    with open('clubs.json', 'r+') as f:
        clubs_data = json.load(f)
        clubs_data['clubs'][0]['points'] = "13"  # S'assurer que Simply Lift a 13 points
        f.seek(0)
        json.dump(clubs_data, f, indent=4)
        f.truncate()
    
    # CRUCIAL: Recharger les clubs dans le serveur en mémoire
    server.clubs = server.loadClubs()
    
    # Connexion
    client.post('/showSummary', data={'email': 'john@simplylift.co'})
    
    # Données initiales après restauration
    with open('competitions.json', 'r') as f:
        competitions_data = json.load(f)
        initial_places = int(competitions_data['competitions'][0]['numberOfPlaces'])
    
    with open('clubs.json', 'r') as f:
        clubs_data = json.load(f)
        initial_points = int(clubs_data['clubs'][0]['points'])
        print(f"Points initiaux: {initial_points}")  # Debug
    
    # Vérifier que les points sont bien chargés dans le serveur
    server_club = next((c for c in server.clubs if c['name'] == 'Simply Lift'), None)
    print(f"Points dans le serveur: {server_club['points']}")
    
    try:
        # Première réservation
        first_booking = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Spring Festival',
            'places': '2'
        }, follow_redirects=True)
        
        print(f"Réponse première réservation: {b'Great! Booking complete!' in first_booking.data}")  # Debug
        if b'Great! Booking complete!' not in first_booking.data:
            print(f"Erreur: {first_booking.data}")  # Voir l'erreur complète
        
        assert b'Great! Booking complete!' in first_booking.data, "La première réservation a échoué"
        
        # Lire les valeurs après la première réservation
        with open('competitions.json', 'r') as f:
            competitions_data = json.load(f)
            places_after_first = int(competitions_data['competitions'][0]['numberOfPlaces'])
            print(f"Places après première réservation: {places_after_first}")  # Debug
        
        with open('clubs.json', 'r') as f:
            clubs_data = json.load(f)
            points_after_first = int(clubs_data['clubs'][0]['points'])
            print(f"Points après première réservation: {points_after_first}")  # Debug
        
        # Vérifier directement la mise à jour après la première réservation
        assert places_after_first == initial_places - 2, f"La première réservation n'a pas été correctement enregistrée. Places: {places_after_first}, attendu: {initial_places - 2}"
        assert points_after_first == initial_points - 6, f"Les points n'ont pas été correctement mis à jour après la première réservation"
        
        # Deuxième réservation (même compétition) - Réduire à 2 places au lieu de 3
        second_booking = client.post('/purchasePlaces', data={
            'club': 'Simply Lift',
            'competition': 'Spring Festival',
            'places': '2'  # 2 places au lieu de 3 pour qu'il reste assez de points
        }, follow_redirects=True)
        
        print(f"Réponse deuxième réservation: {b'Great! Booking complete!' in second_booking.data}")  # Debug
        assert b'Great! Booking complete!' in second_booking.data, "La deuxième réservation a échoué"
        
        # Vérifier les mises à jour finales
        with open('competitions.json', 'r') as f:
            competitions_data = json.load(f)
            updated_places = int(competitions_data['competitions'][0]['numberOfPlaces'])
            print(f"Places après deuxième réservation: {updated_places}")  # Debug
        
        with open('clubs.json', 'r') as f:
            clubs_data = json.load(f)
            updated_points = int(clubs_data['clubs'][0]['points'])
            print(f"Points après deuxième réservation: {updated_points}")  # Debug
        
        # Vérifier le total des modifications (2 + 2 = 4 places, 6 + 6 = 12 points)
        assert updated_places == initial_places - 4, f"Places attendues: {initial_places - 4}, Actuelles: {updated_places}"
        assert updated_points == initial_points - 12, f"Points attendus: {initial_points - 12}, Actuels: {updated_points}"
    
    finally:
        # Restaurer les données originales
        with open('competitions.json', 'r+') as f:
            data = json.load(f)
            data['competitions'][0]['numberOfPlaces'] = str(initial_places)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
        
        with open('clubs.json', 'r+') as f:
            data = json.load(f)
            data['clubs'][0]['points'] = "13"  # Remettre toujours à 13 points
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
        
        # Modifier directement en mémoire
        for club in server.clubs:
            if club['name'] == 'Simply Lift':
                club['points'] = "13"