import pymongo
from datetime import datetime, timedelta
import bcrypt
from bson import ObjectId

# -----------------------------
# Connexion à MongoDB
# -----------------------------
CLIENT = pymongo.MongoClient('mongodb://localhost:27017/')
DB = CLIENT['gestion_stock']

# -----------------------------
# Fonctions de hash des mots de passe
# -----------------------------
def hash_password(password: str) -> bytes:
    """Hash un mot de passe avec bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password: str, hashed: bytes) -> bool:
    """Vérifie si le mot de passe correspond au hash"""
    return bcrypt.checkpw(password.encode(), hashed)

# -----------------------------
# Utilisateurs / Authentification
# -----------------------------
def add_user(data: dict):
    """Ajoute un utilisateur avec mot de passe hashé"""
    data['mot_de_passe'] = hash_password(data['mot_de_passe'])
    data['date_creation'] = datetime.now()
    result = DB['utilisateurs'].insert_one(data)
    return result.inserted_id

def authenticate_user(email: str, password: str):
    """Vérifie email + mot de passe et retourne les infos utilisateur"""
    user = DB['utilisateurs'].find_one({'email': email})
    if user and check_password(password, user['mot_de_passe']):
        user['_id'] = str(user['_id'])
        del user['mot_de_passe']
        return user
    return None

def get_all_users():
    """Liste tous les utilisateurs (sans mot de passe)"""
    return list(DB['utilisateurs'].find({}, {'mot_de_passe': 0}))

def update_user(user_id, data: dict):
    """Met à jour un utilisateur"""
    if 'mot_de_passe' in data and not data['mot_de_passe'].startswith('$2b$'):
        data['mot_de_passe'] = hash_password(data['mot_de_passe'])
    DB['utilisateurs'].update_one({'_id': ObjectId(user_id)}, {'$set': data})
    log_action('Modification utilisateur', None, f"Utilisateur {data.get('nom', '')}", str(user_id))

def delete_user(user_id):
    """Supprime un utilisateur"""
    DB['utilisateurs'].delete_one({'_id': ObjectId(user_id)})
    log_action('Suppression utilisateur', None, 'Utilisateur supprimé', user_id)

# -----------------------------
# Produits
# -----------------------------
def get_all_products():
    return list(DB['produits'].find())

def add_product(data: dict):
    result = DB['produits'].insert_one(data)
    log_action('Ajout produit', result.inserted_id, data['nom'])
    return result.inserted_id

def update_product(product_id, data: dict):
    DB['produits'].update_one({'_id': ObjectId(product_id)}, {'$set': data})
    log_action('Modification produit', product_id, f"Produit mis à jour: {data['nom']}")

def delete_product(product_id):
    DB['produits'].delete_one({'_id': ObjectId(product_id)})
    log_action('Suppression produit', product_id, 'Produit supprimé')

# -----------------------------
# Fournisseurs
# -----------------------------
def get_all_suppliers():
    return list(DB['fournisseurs'].find())

def add_supplier(data: dict):
    result = DB['fournisseurs'].insert_one(data)
    log_action('Ajout fournisseur', None, data['nom_fournisseur'])
    return result.inserted_id

def update_supplier(supplier_id, data: dict):
    DB['fournisseurs'].update_one({'_id': ObjectId(supplier_id)}, {'$set': data})
    log_action('Modification fournisseur', None, data['nom_fournisseur'])

def delete_supplier(supplier_id):
    DB['fournisseurs'].delete_one({'_id': ObjectId(supplier_id)})
    log_action('Suppression fournisseur', None, 'Fournisseur supprimé')

# -----------------------------
# Catégories
# -----------------------------
def get_all_categories():
    return list(DB['categories'].find())

def add_category(data: dict):
    result = DB['categories'].insert_one(data)
    log_action('Ajout catégorie', None, data['nom_categorie'])
    return result.inserted_id

def update_category(category_id, data: dict):
    DB['categories'].update_one({'_id': ObjectId(category_id)}, {'$set': data})
    log_action('Modification catégorie', None, data['nom_categorie'])

def delete_category(category_id):
    DB['categories'].delete_one({'_id': ObjectId(category_id)})
    log_action('Suppression catégorie', None, 'Catégorie supprimée')

# -----------------------------
# Entrées / Sorties de stock
# -----------------------------
def add_entry(data: dict):
    """Ajoute une entrée de stock et met à jour la quantité"""
    result = DB['entrees_stock'].insert_one(data)
    DB['produits'].update_one(
        {'_id': ObjectId(data['produit_id'])},
        {'$inc': {'quantite_stock': data['quantite_entree']}}
    )
    log_action('Entrée stock', data['produit_id'], f"Quantité: {data['quantite_entree']}")
    return result.inserted_id

def add_exit(data: dict):
    """Ajoute une sortie de stock et met à jour la quantité"""
    product = DB['produits'].find_one({'_id': ObjectId(data['produit_id'])})
    if not product:
        raise ValueError("Produit introuvable")
    if product['quantite_stock'] < data['quantite_sortie']:
        raise ValueError("Stock insuffisant")
    result = DB['sorties_stock'].insert_one(data)
    DB['produits'].update_one(
        {'_id': ObjectId(data['produit_id'])},
        {'$inc': {'quantite_stock': -data['quantite_sortie']}}
    )
    log_action('Sortie stock', data['produit_id'], f"Quantité: {data['quantite_sortie']}")
    return result.inserted_id

def get_all_entries():
    return list(DB['entrees_stock'].find())

def get_all_exits():
    return list(DB['sorties_stock'].find())

# -----------------------------
# Historique
# -----------------------------
def log_action(action: str, produit_id=None, details: str='', user_id=None):
    """Ajoute une entrée dans l'historique"""
    DB['historique'].insert_one({
        'action': action,
        'produit_id': produit_id,
        'utilisateur_id': user_id,
        'details': details,
        'date_action': datetime.now()
    })

def get_history(filters=None):
    query = filters or {}
    return list(DB['historique'].find(query).sort('date_action', -1))

# -----------------------------
# Tableau de bord / KPI
# -----------------------------
def get_kpi():
    total_prods = DB['produits'].count_documents({})
    rupture = DB['produits'].count_documents({'quantite_stock': 0})
    recent_entries = DB['entrees_stock'].count_documents({'date_entree': {'$gte': datetime.now() - timedelta(days=30)}})
    recent_exits = DB['sorties_stock'].count_documents({'date_sortie': {'$gte': datetime.now() - timedelta(days=30)}})
    return {
        'total_prods': total_prods,
        'rupture': rupture,
        'recent_entries': recent_entries,
        'recent_exits': recent_exits
    }

def get_stock_by_category():
    """Retourne la quantité totale par catégorie"""
    categories = get_all_categories()
    stock_data = {}
    for cat in categories:
        total = sum(p['quantite_stock'] for p in DB['produits'].find({'categorie': cat['nom_categorie']}))
        stock_data[cat['nom_categorie']] = total
    return stock_data

# -----------------------------
# Fonctions de Recherche
# -----------------------------
def search_products(query: str):
    if not query:
        return get_all_products()
    return list(DB['produits'].find({
        '$or': [
            {'nom': {'$regex': query, '$options': 'i'}},
            {'reference': {'$regex': query, '$options': 'i'}},
            {'categorie': {'$regex': query, '$options': 'i'}}
        ]
    }))

def search_suppliers(query: str):
    if not query:
        return get_all_suppliers()
    return list(DB['fournisseurs'].find({
        '$or': [
            {'nom_fournisseur': {'$regex': query, '$options': 'i'}},
            {'email': {'$regex': query, '$options': 'i'}}
        ]
    }))

def search_categories(query: str):
    if not query:
        return get_all_categories()
    return list(DB['categories'].find({'nom_categorie': {'$regex': query, '$options': 'i'}}))

def search_entries(query: str):
    if not query:
        return get_all_entries()
    return list(DB['entrees_stock'].find({
        '$or': [
            {'produit_id': {'$regex': query, '$options': 'i'}},
            {'date_entree': {'$regex': query, '$options': 'i'}}
        ]
    }))

def search_exits(query: str):
    if not query:
        return get_all_exits()
    return list(DB['sorties_stock'].find({
        '$or': [
            {'produit_id': {'$regex': query, '$options': 'i'}},
            {'destination': {'$regex': query, '$options': 'i'}}
        ]
    }))

def search_history(query: str):
    if not query:
        return get_history()
    return list(DB['historique'].find({
        '$or': [
            {'action': {'$regex': query, '$options': 'i'}},
            {'details': {'$regex': query, '$options': 'i'}}
        ]
    }).sort('date_action', -1))

def search_users(query: str):
    if not query:
        return get_all_users()
    return list(DB['utilisateurs'].find({
        '$or': [
            {'nom': {'$regex': query, '$options': 'i'}},
            {'prenom': {'$regex': query, '$options': 'i'}},
            {'email': {'$regex': query, '$options': 'i'}}
        ]
    }, {'mot_de_passe': 0}))

def get_user(user_id):
    """Récupère un utilisateur par son ID"""
    user = DB['utilisateurs'].find_one({'_id': ObjectId(user_id)}, {'mot_de_passe': 0})
    if user:
        user['_id'] = str(user['_id'])
    return user
