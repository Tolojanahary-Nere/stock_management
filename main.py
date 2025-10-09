import sys
from datetime import datetime
from PySide6.QtWidgets import QApplication, QDialog,QStyleFactory
from database import DB, hash_password
from ui.login import LoginDialog
from ui.main_window import MainWindow
import os

# -------------------------------
# Variables d'environnement pour Linux (éviter les segfaults graphiques)
# -------------------------------
# os.environ["QT_OPENGL"] = "software"
# os.environ["QT_QUICK_BACKEND"] = "software"
# os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"   # très important

if __name__ == '__main__':
    # Créer QApplication
    app = QApplication(sys.argv)
    
    # ===========================
    # Création d'un utilisateur test si la DB est vide
    # ===========================
    if DB['utilisateurs'].count_documents({}) == 0:
        hashed = hash_password('admin')
        DB['utilisateurs'].insert_one({
            'nom': 'Admin',
            'prenom': 'Test',
            'email': 'admin@example.com',
            'role': 'admin',
            'mot_de_passe': hashed,
            'date_creation': datetime.now()
        })
    
    # ===========================
    # Création de données test si nécessaire
    # ===========================
    if DB['categories'].count_documents({}) == 0:
        DB['categories'].insert_one({'nom_categorie': 'Électronique', 'description': 'Appareils électroniques'})
        DB['fournisseurs'].insert_one({'nom_fournisseur': 'Fourn1', 'contact': '123', 'email': 'f1@email.com', 'adresse': 'Addr1'})
        DB['produits'].insert_one({
            'nom': 'Prod1',
            'reference': 'REF1',
            'quantite_stock': 10,
            'prix_unitaire': 100,
            'categorie': 'Électronique',
            'fournisseur': 'Fourn1',
            'date_ajout': datetime.now()
        })
    
    # ===========================
    # Login
    # ===========================
    login = LoginDialog()
    if login.exec() == QDialog.Accepted:
        # ===========================
        # Création de la fenêtre principale
        # ===========================
        window = MainWindow(login.user_id)
        window.show()
        
        # Lancer l'application
        sys.exit(app.exec())
    else:
        sys.exit()
