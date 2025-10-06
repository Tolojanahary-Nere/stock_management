import sys
from PySide6.QtWidgets import QApplication, QDialog  # AJOUTÉ : QDialog ici
from datetime import datetime
from database import (DB, hash_password, get_all_categories, get_all_suppliers, get_all_products)
from ui.login import LoginDialog
from ui.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Créer utilisateur test si nécessaire
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
    
    # Créer données test si nécessaire
    if DB['categories'].count_documents({}) == 0:
        get_all_categories()  # Déclenche insertion si vide, mais adapte
        DB['categories'].insert_one({'nom_categorie': 'Électronique', 'description': 'Appareils électroniques'})
        DB['fournisseurs'].insert_one({'nom_fournisseur': 'Fourn1', 'contact': '123', 'email': 'f1@email.com', 'adresse': 'Addr1'})
        DB['produits'].insert_one({'nom': 'Prod1', 'reference': 'REF1', 'quantite_stock': 10, 'prix_unitaire': 100, 'categorie': 'Électronique', 'fournisseur': 'Fourn1', 'date_ajout': datetime.now()})
    
    login = LoginDialog()
    if login.exec() == QDialog.Accepted:  # Maintenant, QDialog est importé !
        window = MainWindow(login.user_id)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit()