import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    try:
        with open('clubs.json') as c:
            listOfClubs = json.load(c)['clubs']
            return listOfClubs
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error loading clubs: {e}")
        return []


def loadCompetitions():
    try:
        with open('competitions.json') as comps:
            listOfCompetitions = json.load(comps)['competitions']
            return listOfCompetitions
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error loading competitions: {e}")
        return []


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    email = request.form['email']
    try:
        club = [club for club in clubs if club['email'] == email][0]
        return render_template('welcome.html',club=club,competitions=competitions)
    except IndexError:
        flash("Sorry, that email wasn't found.")
        return redirect(url_for('index'))

# Ajoutons une route GET pour showSummary pour le lien retour
@app.route('/showSummary')
def showSummaryGet():
    # Redirection vers l'accueil si accès direct
    return redirect(url_for('index'))


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    
    # NOUVEAU: Vérification si la compétition est complète
    if int(foundCompetition['numberOfPlaces']) <= 0:
        flash("Sorry, this competition is fully booked.")
        return render_template('welcome.html', club=foundClub, competitions=competitions)
        
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=foundClub, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    
    try:
        placesRequired = int(request.form['places'])
        if placesRequired <= 0:
            flash('Please enter a positive number of places.')
            return render_template('booking.html', club=club, competition=competition)
        
        # NOUVEAU: Phase 1 - Limitation de 12 places maximum par réservation
        if placesRequired > 12:
            flash('Cannot book more than 12 places per competition to ensure fairness.')
            return render_template('booking.html', club=club, competition=competition)
            
    except ValueError:
        flash('Please enter a valid number of places.')
        return render_template('booking.html', club=club, competition=competition)
    
    # Phase 0: Gestion des points (1 place = 3 points)
    club_points = int(club['points'])
    points_needed = placesRequired * 3

    if points_needed > club_points:
        flash(f'Not enough points. You need {points_needed} points but only have {club_points}.')
        return render_template('booking.html', club=club, competition=competition)
    
    # Phase 0: Éviter la surréservation
    available_places = int(competition['numberOfPlaces'])
    if placesRequired > available_places:
        flash(f'Not enough places available. Only {available_places} places left.')
        return render_template('booking.html', club=club, competition=competition)
    
    # Mise à jour des données
    competition['numberOfPlaces'] = str(available_places - placesRequired)
    club['points'] = str(club_points - points_needed)
    
    # CORRECTION: Sauvegarde automatique des données
    saveClubs()
    saveCompetitions()
    
    # NOUVEAU: Message de confirmation détaillé
    flash(f'Great! Booking complete! {placesRequired} places booked. {points_needed} points deducted.')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display
@app.route('/points')
def showPoints():
    """Affiche le tableau des points pour tous les clubs (Phase 0)"""
    return render_template('points.html', clubs=clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))

def saveClubs():
    with open('clubs.json', 'w') as c:
        json.dump({"clubs": clubs}, c, indent=4)

def saveCompetitions():
    with open('competitions.json', 'w') as comps:
        json.dump({"competitions": competitions}, comps, indent=4)
if __name__ == '__main__':
    app.run(debug=True)