from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPushButton, QTextEdit, QMessageBox
from PySide6.QtCore import Qt, Signal
from datetime import datetime
from database import (
    get_all_categories, get_all_suppliers, get_all_products, add_product, update_product,
    add_supplier, update_supplier, add_category, update_category, add_entry, add_exit,
    add_user, update_user
)

# ------------------ PRODUCT FORM ------------------
class ProductForm(QDialog):
    saved = Signal()  # signal émis après CRUD
    def __init__(self, parent=None, product=None, user_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Ajouter/Modifier Produit")
        self.setFixedSize(400, 300)
        layout = QFormLayout()
        
        self.nom_input = QLineEdit(product['nom'] if product else '')
        self.ref_input = QLineEdit(product['reference'] if product else '')
        self.categ_combo = QComboBox()
        self.categ_combo.addItems([cat['nom_categorie'] for cat in get_all_categories()])
        if product:
            self.categ_combo.setCurrentText(product.get('categorie', ''))
        self.fourn_combo = QComboBox()
        self.fourn_combo.addItems([fourn['nom_fournisseur'] for fourn in get_all_suppliers()])
        if product:
            self.fourn_combo.setCurrentText(product.get('fournisseur', ''))
        self.quant_input = QSpinBox()
        self.quant_input.setValue(product['quantite_stock'] if product else 0)
        self.prix_input = QDoubleSpinBox()
        self.prix_input.setValue(product['prix_unitaire'] if product else 0.0)
        
        layout.addRow("Nom:", self.nom_input)
        layout.addRow("Référence:", self.ref_input)
        layout.addRow("Catégorie:", self.categ_combo)
        layout.addRow("Fournisseur:", self.fourn_combo)
        layout.addRow("Quantité:", self.quant_input)
        layout.addRow("Prix unitaire:", self.prix_input)
        
        save_btn = QPushButton("Sauvegarder")
        save_btn.clicked.connect(self.save)
        layout.addRow(save_btn)
        
        self.setLayout(layout)
        self.product_id = product['_id'] if product else None

    def save(self):
        data = {
            'nom': self.nom_input.text(),
            'reference': self.ref_input.text(),
            'categorie': self.categ_combo.currentText(),
            'fournisseur': self.fourn_combo.currentText(),
            'quantite_stock': self.quant_input.value(),
            'prix_unitaire': self.prix_input.value(),
            'date_ajout': datetime.now()
        }
        if self.product_id:
            update_product(str(self.product_id), data)
        else:
            add_product(data)
        self.saved.emit()  # ← signal pour notifier MainWindow
        self.accept()

# ------------------ ENTRY FORM ------------------
class EntryForm(QDialog):
    saved = Signal()
    def __init__(self, parent=None, user_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Nouvelle Entrée")
        self.setFixedSize(400, 300)
        layout = QFormLayout()
        
        self.prod_combo = QComboBox()
        self.prod_combo.addItems([f"{p['nom']} ({p['reference']})" for p in get_all_products()])
        self.fourn_combo = QComboBox()
        self.fourn_combo.addItems([f['nom_fournisseur'] for f in get_all_suppliers()])
        self.quant_input = QSpinBox()
        self.prix_input = QDoubleSpinBox()
        
        layout.addRow("Produit:", self.prod_combo)
        layout.addRow("Fournisseur:", self.fourn_combo)
        layout.addRow("Quantité:", self.quant_input)
        layout.addRow("Prix achat:", self.prix_input)
        
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.save)
        layout.addRow(save_btn)
        
        self.setLayout(layout)

    def save(self):
        if self.prod_combo.currentText() == '':
            QMessageBox.warning(self, "Erreur", "Sélectionnez un produit")
            return
        prod_name = self.prod_combo.currentText().split(' (')[0]
        product = next((p for p in get_all_products() if p['nom'] == prod_name), None)
        if not product:
            QMessageBox.warning(self, "Erreur", "Produit non trouvé")
            return
        if self.fourn_combo.currentText() == '':
            QMessageBox.warning(self, "Erreur", "Sélectionnez un fournisseur")
            return
        fourn_name = self.fourn_combo.currentText()
        fournisseur = next((f for f in get_all_suppliers() if f['nom_fournisseur'] == fourn_name), None)
        if not fournisseur:
            QMessageBox.warning(self, "Erreur", "Fournisseur non trouvé")
            return
        
        data = {
            'produit_id': str(product['_id']),
            'fournisseur_id': str(fournisseur['_id']),
            'quantite_entree': self.quant_input.value(),
            'prix_achat_unitaire': self.prix_input.value(),
            'date_entree': datetime.now()
        }
        try:
            add_entry(data)
            self.saved.emit()
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Erreur", str(e))

# ------------------ EXIT FORM ------------------
class ExitForm(QDialog):
    saved = Signal()
    def __init__(self, parent=None, user_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Nouvelle Sortie")
        self.setFixedSize(400, 250)
        layout = QFormLayout()
        
        self.prod_combo = QComboBox()
        self.prod_combo.addItems([f"{p['nom']} ({p['reference']})" for p in get_all_products()])
        self.quant_input = QSpinBox()
        self.dest_input = QLineEdit("Vente")
        
        layout.addRow("Produit:", self.prod_combo)
        layout.addRow("Quantité:", self.quant_input)
        layout.addRow("Destination:", self.dest_input)
        
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.save)
        layout.addRow(save_btn)
        
        self.setLayout(layout)

    def save(self):
        if self.prod_combo.currentText() == '':
            QMessageBox.warning(self, "Erreur", "Sélectionnez un produit")
            return
        prod_name = self.prod_combo.currentText().split(' (')[0]
        product = next((p for p in get_all_products() if p['nom'] == prod_name), None)
        if not product:
            QMessageBox.warning(self, "Erreur", "Produit non trouvé")
            return
        
        data = {
            'produit_id': str(product['_id']),
            'quantite_sortie': self.quant_input.value(),
            'date_sortie': datetime.now(),
            'destination': self.dest_input.text()
        }
        try:
            add_exit(data)
            self.saved.emit()
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Erreur", str(e))

# ------------------ SUPPLIER FORM ------------------
class SupplierForm(QDialog):
    saved = Signal()
    def __init__(self, parent=None, supplier=None, user_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Ajouter/Modifier Fournisseur")
        self.setFixedSize(400, 300)
        layout = QFormLayout()
        
        self.nom_input = QLineEdit(supplier['nom_fournisseur'] if supplier else '')
        self.contact_input = QLineEdit(supplier['contact'] if supplier else '')
        self.email_input = QLineEdit(supplier['email'] if supplier else '')
        self.adresse_input = QTextEdit(supplier['adresse'] if supplier else '')
        
        layout.addRow("Nom:", self.nom_input)
        layout.addRow("Contact:", self.contact_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Adresse:", self.adresse_input)
        
        save_btn = QPushButton("Sauvegarder")
        save_btn.clicked.connect(self.save)
        layout.addRow(save_btn)
        
        self.setLayout(layout)
        self.supplier_id = supplier['_id'] if supplier else None

    def save(self):
        data = {
            'nom_fournisseur': self.nom_input.text(),
            'contact': self.contact_input.text(),
            'email': self.email_input.text(),
            'adresse': self.adresse_input.toPlainText()
        }
        if self.supplier_id:
            update_supplier(str(self.supplier_id), data)
        else:
            add_supplier(data)
        self.saved.emit()
        self.accept()

# ------------------ CATEGORY FORM ------------------
class CategoryForm(QDialog):
    saved = Signal()
    def __init__(self, parent=None, category=None, user_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Ajouter/Modifier Catégorie")
        self.setFixedSize(300, 200)
        layout = QFormLayout()
        
        self.nom_input = QLineEdit(category['nom_categorie'] if category else '')
        self.desc_input = QTextEdit(category['description'] if category else '')
        
        layout.addRow("Nom:", self.nom_input)
        layout.addRow("Description:", self.desc_input)
        
        save_btn = QPushButton("Sauvegarder")
        save_btn.clicked.connect(self.save)
        layout.addRow(save_btn)
        
        self.setLayout(layout)
        self.category_id = category['_id'] if category else None

    def save(self):
        data = {
            'nom_categorie': self.nom_input.text(),
            'description': self.desc_input.toPlainText()
        }
        if self.category_id:
            update_category(str(self.category_id), data)
        else:
            add_category(data)
        self.saved.emit()
        self.accept()

# ------------------ USER FORM ------------------
class UserForm(QDialog):
    saved = Signal()
    def __init__(self, parent=None, user=None, current_user_id=None):
        super().__init__(parent)
        self.current_user_id = current_user_id  # Pour éviter de se supprimer soi-même
        self.setWindowTitle("Ajouter/Modifier Utilisateur")
        self.setFixedSize(400, 350)
        layout = QFormLayout()
        
        self.nom_input = QLineEdit(user['nom'] if user else '')
        self.prenom_input = QLineEdit(user['prenom'] if user else '')
        self.email_input = QLineEdit(user['email'] if user else '')
        self.role_combo = QComboBox()
        self.role_combo.addItems(['admin', 'user', 'manager'])
        if user:
            self.role_combo.setCurrentText(user.get('role', 'user'))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Nouveau mot de passe (obligatoire pour ajout, optionnel pour modification)")
        
        layout.addRow("Nom:", self.nom_input)
        layout.addRow("Prénom:", self.prenom_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Rôle:", self.role_combo)
        layout.addRow("Mot de passe:", self.password_input)
        
        save_btn = QPushButton("Sauvegarder")
        save_btn.clicked.connect(self.save)
        layout.addRow(save_btn)
        
        self.setLayout(layout)
        self.user_id = user['_id'] if user else None

    def save(self):
        if not self.nom_input.text() or not self.prenom_input.text() or not self.email_input.text():
            QMessageBox.warning(self, "Erreur", "Remplissez tous les champs obligatoires")
            return
        password = self.password_input.text()
        if not password and not self.user_id:
            QMessageBox.warning(self, "Erreur", "Mot de passe obligatoire pour un nouvel utilisateur")
            return
        data = {
            'nom': self.nom_input.text(),
            'prenom': self.prenom_input.text(),
            'email': self.email_input.text(),
            'role': self.role_combo.currentText()
        }
        if password:
            data['mot_de_passe'] = password  # Sera hashé dans add_user/update_user
        
        if self.user_id:
            update_user(str(self.user_id), data)
        else:
            add_user(data)
        self.saved.emit()
        self.accept()
