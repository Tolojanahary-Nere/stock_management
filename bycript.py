from database import DB, hash_password
from datetime import datetime

# 1️⃣ Supprimer tous les utilisateurs existants
DB['utilisateurs'].delete_many({})

# 2️⃣ Créer un nouvel admin
admin = {
    'nom': 'Tojo',
    'prenom': 'Nere',
    'email': 'tojonere@gmail.com',
    'role': 'admin',
    'mot_de_passe': hash_password('nere@2025'),  # Hash bcrypt
    'date_creation': datetime.now()
}

result = DB['utilisateurs'].insert_one(admin)
print(f"Nouvel admin créé avec _id : {result.inserted_id}")
