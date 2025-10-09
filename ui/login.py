from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QMessageBox, 
    QVBoxLayout, QLabel, QHBoxLayout, QGraphicsOpacityEffect,
)
from PySide6.QtCore import Qt, QPropertyAnimation
from PySide6.QtGui import QIcon, QFont,QAction
from database import authenticate_user


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connexion")
        self.setFixedSize(400, 320)
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        
        # 🎨 Fond dégradé doux
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1f4037, stop:1 #99f2c8);
                border-radius: 12px;
            }
        """)

        # 🪟 Animation d’apparition
        self.fade_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.fade_effect)
        self.fade_animation = QPropertyAnimation(self.fade_effect, b"opacity")
        self.fade_animation.setDuration(700)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.start()

        # 🎨 Carte centrale (effet "glassmorphism")
        self.card = QVBoxLayout()
        self.card.setContentsMargins(35, 35, 35, 35)
        self.card.setSpacing(25)

        # 🔠 Titre
        title_label = QLabel("Bienvenue 👋")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title_label.setStyleSheet("color: white; letter-spacing: 1px;")
        self.card.addWidget(title_label)

        # 📋 Formulaire
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        input_style = """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 10px 36px 10px 12px;
                color: white;
                font-size: 14px;
            }
            QLineEdit::placeholder {
                color: rgba(255,255,255,0.6);
            }
        """

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Adresse e-mail")
        self.email_input.setStyleSheet(input_style)
        mail_icon = QAction(QIcon.fromTheme("mail-message-new"), "", self)
        self.email_input.addAction(mail_icon, QLineEdit.TrailingPosition)

        # Mot de passe
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setStyleSheet(input_style)

        # 👁️ Icône pour afficher/masquer le mot de passe
        toggle_action = QAction(QIcon.fromTheme("view-password"), "", self)
        toggle_action.triggered.connect(self.toggle_password_visibility)
        self.password_input.addAction(toggle_action, QLineEdit.TrailingPosition)
        self.password_visible = False

        form_layout.addRow("Email :", self.email_input)
        form_layout.addRow("Mot de passe :", self.password_input)
        self.card.addLayout(form_layout)

        # 🔘 Bouton de connexion
        self.login_btn = QPushButton("Se connecter")
        self.login_btn.clicked.connect(self.login)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                border: none;
                padding: 12px;
                border-radius: 8px;
                color: white;
                font-size: 15px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #1abc9c;
            }
        """)
        self.card.addWidget(self.login_btn)

        # 🔗 Lien mot de passe oublié
        forgot_label = QLabel("<a href='#' style='color:white; text-decoration:none;'>Mot de passe oublié ?</a>")
        forgot_label.setAlignment(Qt.AlignCenter)
        forgot_label.setOpenExternalLinks(False)
        forgot_label.linkActivated.connect(self.show_forgot_message)
        self.card.addWidget(forgot_label)

        # Appliquer la mise en page principale
        self.setLayout(self.card)
        self.user_id = None


    def toggle_password_visibility(self):
        """Afficher ou masquer le mot de passe."""
        if self.password_visible:
            self.password_input.setEchoMode(QLineEdit.Password)
        else:
            self.password_input.setEchoMode(QLineEdit.Normal)
        self.password_visible = not self.password_visible


    def show_forgot_message(self):
        QMessageBox.information(self, "Mot de passe oublié",
                                "Veuillez contacter l'administrateur pour réinitialiser votre mot de passe.")


    def login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir email et mot de passe")
            return

        user = authenticate_user(email, password)
        if user:
            self.user_id = str(user['_id'])
            QMessageBox.information(self, "Succès", f"Bienvenue {user.get('prenom', '')} !")
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", "Identifiants incorrects")
