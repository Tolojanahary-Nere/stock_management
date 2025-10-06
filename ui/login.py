# login.py
from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QMessageBox
from database import authenticate_user

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connexion")
        self.setFixedSize(300, 200)

        layout = QFormLayout()
        
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        layout.addRow("Email:", self.email_input)
        layout.addRow("Mot de passe:", self.password_input)
        
        login_btn = QPushButton("Se connecter")
        login_btn.clicked.connect(self.login)
        layout.addRow(login_btn)
        
        self.setLayout(layout)
        self.user_id = None

    def login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir email et mot de passe")
            return

        user = authenticate_user(email, password)  # On récupère le dictionnaire utilisateur

        if user:
            self.user_id = str(user['_id'])  # 🔥 On garde uniquement l'ID sous forme de chaîne
            QMessageBox.information(self, "Succès", f"Bienvenue {user.get('prenom', '')} !")
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", "Identifiants incorrects")
