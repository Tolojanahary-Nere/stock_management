from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox
from database import get_all_users, delete_user, search_users
from .forms import UserForm

class UsersMixin:
    def create_user_widget(self):
        self.user_table = QTableWidget()
        headers = ['Nom', 'Prénom', 'Email', 'Rôle']
        columns_map = {'Nom': 'nom', 'Prénom': 'prenom', 'Email': 'email', 'Rôle': 'role'}
        return self.create_crud_widget(self.user_table, self.load_users_data, self.load_users, search_users, UserForm, self.delete_user_safe, headers, columns_map, 'Utilisateurs')

    def load_users_data(self):
        return get_all_users()

    def load_users(self):
        users = self.load_users_data()
        self.user_table.setRowCount(len(users))
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels(['Nom', 'Prénom', 'Email', 'Rôle', 'ID'])
        self.user_table.setColumnHidden(4, True)
        for i, u in enumerate(users):
            self.user_table.setItem(i, 0, QTableWidgetItem(u.get('nom', '')))
            self.user_table.setItem(i, 1, QTableWidgetItem(u.get('prenom', '')))
            self.user_table.setItem(i, 2, QTableWidgetItem(u.get('email', '')))
            self.user_table.setItem(i, 3, QTableWidgetItem(u.get('role', '')))
            self.user_table.setItem(i, 4, QTableWidgetItem(str(u['_id'])))

    def delete_user_safe(self, user_id):
        if str(user_id) == self.user_id:
            QMessageBox.warning(self, "Erreur", "Vous ne pouvez pas supprimer votre propre compte")
            return
        delete_user(str(user_id))