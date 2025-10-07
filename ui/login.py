# login.py
from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from database import authenticate_user

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connexion")
        self.setFixedSize(350, 250)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1e3c72, stop:1 #2a5298);
                border-radius: 10px;
            }
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #34495e;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 10px;
                color: white;
            }
            QPushButton {
                background-color: #3498db;
                border: none;
                padding: 12px;
                border-radius: 6px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        title_label = QLabel("Bienvenue !")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Entrez votre email")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Mot de passe:", self.password_input)
        
        main_layout.addLayout(form_layout)
        
        login_btn = QPushButton("Se connecter")
        login_btn.clicked.connect(self.login)
        main_layout.addWidget(login_btn)
        
        self.setLayout(main_layout)
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