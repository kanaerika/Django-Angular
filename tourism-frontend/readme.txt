DOCUMENTATION COMPLÈTE DU BACKEND - SYSTÈME DE TOURISME
📋 TABLE DES MATIÈRES
Architecture Générale

Applications et leurs Rôles

Guide des URLs par Application

Guide des Tâches Courantes

Exemples de Requêtes

Sécurité et Permissions

🏗️ ARCHITECTURE GÉNÉRALE {#architecture}
Le backend est construit avec Django REST Framework et suit une architecture micro-services interne où chaque application a une responsabilité unique et spécifique.

text
tourism_system/
│
├── core/           ← Outils partagés (modèles abstraits, mixins)
├── account/        ← Gestion des utilisateurs et authentification
├── destinations/   ← Gestion des  villes
├── tour/           ← Gestion des activités touristiques
├── reviews/        ← Gestion des avis et notations
├── booking/        ← Gestion des réservations et paiements
└── tourism/        ← Gestion des hôtels (module complémentaire)
Flux de données principal
text
Utilisateur → Authentification (account) → Création activité (tour) 
→ Réservation (booking) → Avis (reviews) → Destinations (destinations)
📱 APPLICATIONS ET LEURS RÔLES {#applications}
1. CORE - Coeur du système
Rôle: Fournir des composants réutilisables à toutes les applications

Composant	Description
TimeStampedModel	Ajoute automatiquement created_at et updated_at à tous les modèles
SoftDeleteModel	Permet la suppression logique (sans effacer les données)
StandardPagination	Pagination par défaut (10 éléments/page)
CacheMixin	Met en cache les réponses des vues
ActionSerializerMixin	Permet d'utiliser différents sérializers par action
2. ACCOUNT - Gestion des utilisateurs
Rôle: Authentification, autorisation et gestion des profils utilisateurs

Modèles principaux:
Modèle	Description
Role	Définit les permissions (Admin, Guide, Tourist)
CustomUser	Utilisateur étendu avec rôle et infos personnelles
Profile	Informations supplémentaires (téléphone, avatar, bio)
URLs principales:
Méthode	URL	Description	Permissions
POST	/api/auth/users/	Créer un compte	Public
POST	/api/auth/login/	Se connecter (reçoit tokens)	Public
POST	/api/auth/logout/	Se déconnecter	Authentifié
GET	/api/auth/users/me/	Voir son profil	Authentifié
PUT/PATCH	/api/auth/users/me/	Modifier son profil	Authentifié
POST	/api/auth/users/change-password/	Changer mot de passe	Authentifié
GET	/api/auth/users/	Lister utilisateurs	Admin
POST	/api/auth/users/{id}/assign-role/	Assigner un rôle	Admin
GET/PUT/DELETE	/api/auth/profiles/me/	Gérer son profil	Authentifié
Rôles et permissions:
Rôle	ID	Permissions
Admin	1	Accès total à tout le système
Guide	2	Créer/modifier ses activités
Tourist	3	Réserver, avis, consultation
3. DESTINATIONS -  Villes
Rôle: Gestion géographique des destinations touristiques

Modèles:
Modèle	Description
Country	Pays (nom, code ISO)
City	Ville avec coordonnées GPS, description, photo
URLs:
Méthode	URL	Description
GET	/api/destinations/countries/	Lister tous les pays
POST	/api/destinations/countries/	Créer un pays (Admin/Guide)
GET	/api/destinations/countries/{id}/	Détail d'un pays
GET	/api/destinations/countries/{id}/cities/	Villes d'un pays
GET	/api/destinations/countries/popular/	Pays populaires
GET	/api/destinations/cities/	Lister villes (filtrable)
POST	/api/destinations/cities/	Créer ville (Admin/Guide)
GET	/api/destinations/cities/{id}/activities/	Activités d'une ville
GET	/api/destinations/cities/featured/	Villes en vedette
GET	/api/destinations/cities/search/?q=paris	Rechercher ville
Paramètres de filtrage pour /cities/:
text
?country=1              → Filtrer par pays
?search=paris           → Recherche textuelle
?order_by_activities=desc → Trier par nombre d'activités
?order_by_rating=desc   → Trier par note moyenne
4. TOUR - Activités touristiques
Rôle: Cœur du système - gestion des activités, créneaux et catégories

Modèles:
Modèle	Description
Category	Catégorie d'activité (Visite historique, Aventure...)
Activity	Activité principale (titre, prix, durée, description)
ActivityImage	Galerie d'images pour l'activité
Schedule	Créneaux horaires disponibles
URLs:
Méthode	URL	Description
GET/POST	/api/tour/categories/	Lister/créer catégories
GET	/api/tour/categories/{slug}/activities/	Activitès par catégorie
GET/POST	/api/tour/activities/	Lister/créer activités
GET	/api/tour/activities/{slug}/	Détail d'une activité
PUT/DELETE	/api/tour/activities/{slug}/	Modifier/supprimer
GET	/api/tour/activities/{slug}/schedules/	Créneaux de l'activité
GET	/api/tour/activities/{slug}/available-schedules/	Créneaux disponibles
POST	/api/tour/activities/{slug}/images/	Ajouter image
GET	/api/tour/activities/featured/	Activités vedettes
GET	/api/tour/activities/popular/	Activités populaires
GET	/api/tour/schedules/	Lister créneaux
POST	/api/tour/schedules/	Créer créneau
Paramètres de filtrage pour /activities/:
text
?city=paris              → Ville
?country=FR              → Pays
?category=aventures      → Catégorie
?search=réunion          → Recherche
?min_price=10&max_price=100 → Fourchette prix
?min_duration=2&max_duration=6 → Durée
?ordering=price          → Tri (price, rating, duration)
?ordering=-price         → Tri descendant
5. REVIEWS - Avis et notations
Rôle: Gestion des avis des touristes sur les activités

Modèle:
Modèle	Description
Review	Avis (note 1-5, titre, commentaire, modération)
URLs:
Méthode	URL	Description
GET/POST	/api/reviews/reviews/	Lister/déposer avis
GET/PUT/DELETE	/api/reviews/reviews/{id}/	Gérer un avis
GET	/api/reviews/reviews/my-reviews/	Mes avis
GET	/api/reviews/reviews/pending/	Avis à modérer (Admin)
PUT/PATCH	/api/reviews/reviews/{id}/moderate/	Modérer avis (Admin)
GET	/api/reviews/reviews/activity/{slug}/ratings/	Statistiques notes
Règles métier:
1 utilisateur = 1 avis par activité

L'avis n'apparaît qu'après validation (is_visible=True)

La note moyenne est automatiquement mise en cache (cached_rating)

6. BOOKING - Réservations
Rôle: Gestion des réservations et paiements

Modèles:
Modèle	Description
Booking	Réservation avec référence unique, statut
Payment	Paiement associé à une réservation
URLs:
Méthode	URL	Description
GET/POST	/api/bookings/bookings/	Lister/réserver
GET	/api/bookings/bookings/my-stats/	Mes statistiques
GET	/api/bookings/bookings/upcoming/	Réservations à venir
GET	/api/bookings/bookings/past/	Réservations passées
POST	/api/bookings/bookings/{id}/cancel/	Annuler réservation
POST	/api/bookings/bookings/{id}/pay/	Payer réservation
PUT/PATCH	/api/bookings/bookings/{id}/status/	Changer statut (Admin)
GET	/api/bookings/payments/	Lister paiements
Statuts de réservation:
Statut	Signification
pending	En attente de paiement
confirmed	Confirmée, paiement reçu
completed	Terminée (peut laisser avis)
cancelled	Annulée
refunded	Remboursée
Fonctionnalités automatiques:
total_price calculé automatiquement

booking_reference (UUID) généré

available_spots mis à jour automatiquement

7. TOURISM - Hôtels (module complémentaire)
Rôle: Gestion des hébergements et réservations hôtelières

Modèles:
Modèle	Description
Destination	Destination touristique
Hotel	Hôtel dans une destination
HotelBooking	Réservation hôtelière
DestinationReview	Avis sur destination
URLs:
Méthode	URL	Description
GET/POST	/api/tourism/destinations/	Gérer destinations
GET	/api/tourism/destinations/{id}/hotels/	Hôtels par destination
GET/POST	/api/tourism/hotels/	Gérer hôtels
GET/POST	/api/tourism/hotel-bookings/	Réserver hôtel
GET	/api/tourism/hotel-bookings/my-bookings/	Mes réservations
POST	/api/tourism/hotel-bookings/{id}/cancel/	Annuler
GET/POST	/api/tourism/destination-reviews/	Avis destinations
🎯 GUIDE DES TÂCHES COURANTES {#taches}
Tâche 1: Créer un compte utilisateur
Étapes:

Envoyer POST à /api/auth/users/

Récupérer la réponse

Se connecter pour obtenir les tokens

Requête:

json
POST /api/auth/users/
{
    "username": "jean_dupont",
    "email": "jean@email.com",
    "password": "MotDePasse123!",
    "password2": "MotDePasse123!",
    "first_name": "Jean",
    "last_name": "Dupont"
}
Tâche 2: Se connecter
Requête:

json
POST /api/auth/login/
{
    "username": "jean_dupont",
    "password": "MotDePasse123!"
}
Réponse:

json
{
    "refresh": "eyJhbGc...",
    "access": "eyJhbGc...",
    "user": {...}
}
Tâche 3: Créer une activité (en tant que Guide)
Prérequis: Avoir un token d'accès

Étapes:

Créer d'abord un pays: POST /api/destinations/countries/

Créer une ville: POST /api/destinations/cities/

Créer des catégories: POST /api/tour/categories/

Créer l'activité

Requête:

bash
POST /api/tour/activities/
Authorization: Bearer votre_token
Content-Type: application/json

{
    "title": "Visite du Louvre",
    "city": 1,
    "categories": [1, 2],
    "description": "Découvrez les chefs-d'œuvre du Louvre...",
    "base_price": 45.00,
    "max_travelers": 15,
    "duration_hours": 2.5,
    "is_active": true
}
Tâche 4: Ajouter des créneaux à une activité
Requête:

json
POST /api/tour/schedules/
Authorization: Bearer votre_token

{
    "activity": 1,
    "date": "2026-06-15",
    "start_time": "14:00:00",
    "available_spots": 10,
    "price_override": 50.00
}
Tâche 5: Réserver une activité
Prérequis: Être connecté en tant que Tourist

Requête:

json
POST /api/bookings/bookings/
Authorization: Bearer token_tourist

{
    "schedule": 1,
    "number_of_travelers": 2,
    "special_requests": "Végétarien"
}
Tâche 6: Payer une réservation
Requête:

json
POST /api/bookings/bookings/1/pay/
Authorization: Bearer token_tourist

{
    "method": "stripe",
    "stripe_payment_intent_id": "pi_xxx"
}
Tâche 7: Laisser un avis
Prérequis: Réservation terminée

Requête:

json
POST /api/reviews/reviews/
Authorization: Bearer token_tourist

{
    "activity": 1,
    "rating": 5,
    "title": "Expérience incroyable !",
    "comment": "Guide très compétent..."
}
Tâche 8: Rechercher des activités
Requête GET avec paramètres:

text
GET /api/tour/activities/?city=paris&category=aventures&min_price=20&max_price=100&ordering=-rating
Tâche 9: Voir les disponibilités d'une activité
Requête:

text
GET /api/tour/activities/{slug}/available-schedules/
Tâche 10: Annuler une réservation
Requête:

json
POST /api/bookings/bookings/1/cancel/
Authorization: Bearer token_tourist

{
    "reason": "Changement de plan"
}
📡 EXEMPLES DE REQUÊTES COMPLÈTES {#requetes}
Avec cURL
bash
# 1. Se connecter
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "jean", "password": "pass123"}'

# 2. Créer une activité
curl -X POST http://localhost:8000/api/tour/activities/ \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"title": "Randonnée", "city": 1, "base_price": 30, "duration_hours": 3}'

# 3. Lister les activités
curl http://localhost:8000/api/tour/activities/?city=paris

# 4. Réserver
curl -X POST http://localhost:8000/api/bookings/bookings/ \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"schedule": 1, "number_of_travelers": 2}'
Avec JavaScript/Fetch
javascript
// Configuration
const API_URL = 'http://localhost:8000/api';
let accessToken = null;

// Connexion
async function login(username, password) {
    const response = await fetch(`${API_URL}/auth/login/`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    });
    const data = await response.json();
    accessToken = data.access;
    return data;
}

// Créer activité
async function createActivity(activityData) {
    const response = await fetch(`${API_URL}/tour/activities/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(activityData)
    });
    return await response.json();
}

// Rechercher activités
async function searchActivities(params) {
    const query = new URLSearchParams(params).toString();
    const response = await fetch(`${API_URL}/tour/activities/?${query}`);
    return await response.json();
}

// Réserver
async function createBooking(scheduleId, travelers) {
    const response = await fetch(`${API_URL}/bookings/bookings/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            schedule: scheduleId,
            number_of_travelers: travelers
        })
    });
    return await response.json();
}

// Utilisation
await login('jean', 'pass123');
await createActivity({
    title: 'Visite guidée',
    city: 1,
    base_price: 45,
    duration_hours: 2
});
Avec Python/Requests
python
import requests

BASE_URL = "http://localhost:8000/api"
token = None

def login(username, password):
    global token
    response = requests.post(f"{BASE_URL}/auth/login/", 
                            json={"username": username, "password": password})
    token = response.json()["access"]
    return response.json()

def create_activity(data):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/tour/activities/", 
                            json=data, headers=headers)
    return response.json()

def search_activities(city=None, category=None):
    params = {}
    if city: params["city"] = city
    if category: params["category"] = category
    response = requests.get(f"{BASE_URL}/tour/activities/", params=params)
    return response.json()

# Utilisation
login("jean", "pass123")
activity = create_activity({
    "title": "Randonnée",
    "city": 1,
    "base_price": 30,
    "duration_hours": 3
})
activities = search_activities(city="paris")
🔐 SÉCURITÉ ET PERMISSIONS {#securite}
Hiérarchie des permissions
Permission	GET (lecture)	POST (création)	PUT (modif)	DELETE
Public (non connecté)	✅	❌	❌	❌
Tourist (connecté)	✅	✅ (limité)	✅ (ses données)	❌
Guide	✅	✅ (ses activités)	✅ (ses activités)	✅ (ses activités)
Admin	✅	✅ (tout)	✅ (tout)	✅ (tout)
Tokens JWT
Access Token: Valide 1 jour

Refresh Token: Valide 7 jours

Header requis: Authorization: Bearer <access_token>

Obtenir un nouveau token
json
POST /api/token/refresh/
{
    "refresh": "votre_refresh_token"
}
📊 RÉSUMÉ DES RÔLES DES APPLICATIONS
Application	Responsabilité principale	Dépend de
core	Utilitaires partagés	Aucune
account	Utilisateurs, rôles, auth	core
destinations	Pays, villes	core
tour	Activités, catégories, créneaux	core, destinations
reviews	Avis, notations	core, account, tour
booking	Réservations, paiements	core, account, tour
tourism	Hôtels (extension)	core, account
🚀 FLUX COMPLET D'UNE RÉSERVATION
text
1. Tourist s'inscrit → POST /api/auth/users/
2. Tourist se connecte → POST /api/auth/login/
3. Tourist cherche activités → GET /api/tour/activities/?city=paris
4. Tourist voit détail → GET /api/tour/activities/visite-louvre/
5. Tourist choisit créneau → GET /api/tour/activities/visite-louvre/available-schedules/
6. Tourist réserve → POST /api/bookings/bookings/
7. Tourist paie → POST /api/bookings/bookings/1/pay/
8. Statut devient "confirmed"
9. Activité terminée → Admin met statut "completed"
10. Tourist laisse avis → POST /api/reviews/reviews/
11. Note moyenne mise à jour automatiquement
🔧 VARIABLES D'ENVIRONNEMENT RECOMMANDÉES
env
# .env
DEBUG=True
SECRET_KEY=votre_cle_secrete
DATABASE_URL=sqlite:///db.sqlite3

# Pour la production
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre_email
EMAIL_HOST_PASSWORD=votre_password

# Stripe (paiements)
STRIPE_PUBLIC_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx
✅ VÉRIFICATION RAPIDE
Pour tester que tout fonctionne:

bash
# 1. Démarrer le serveur
python manage.py runserver

# 2. Vérifier les endpoints publics
curl http://localhost:8000/api/tour/activities/
curl http://localhost:8000/api/destinations/countries/

# 3. Créer un compte
curl -X POST http://localhost:8000/api/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"Test123!","password2":"Test123!"}'

# 4. Se connecter
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"Test123!"}'
Cette documentation couvre l'intégralité du backend. Chaque application est indépendante mais interconnectée, suivant le principe de responsabilité unique. Les URLs sont RESTful et cohérentes dans tout le système.