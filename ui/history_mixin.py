from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from datetime import datetime
from database import get_history, delete_history, search_history
from .forms import UserForm

class HistoryMixin:
    def create_history_widget(self):
        self.history_table = QTableWidget()
        headers = ['Action', 'Produit', 'Rôle Utilisateur', 'Date']
        columns_map = {'Action': 'action', 'Produit': 'produit_nom', 'Rôle Utilisateur': 'role', 'Date': 'date_action'}
        return self.create_crud_widget(self.history_table, self.load_history_data, self.load_history, search_history, UserForm, delete_history, headers, columns_map, 'Historique', enable_edit=False)

    def load_history_data(self):
        return get_history()

    def load_history(self):
        history = self.load_history_data()
        history = self.enrich_data(history, {'Produit': 'produit_nom', 'Rôle Utilisateur': 'role'})
        self.history_table.setRowCount(len(history))
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(['Action', 'Produit', 'Rôle Utilisateur', 'Date', 'ID'])
        self.history_table.setColumnHidden(4, True)
        for i, h in enumerate(history):
            self.history_table.setItem(i, 0, QTableWidgetItem(h.get('action', '')))
            self.history_table.setItem(i, 1, QTableWidgetItem(h.get('produit_nom', '')))
            self.history_table.setItem(i, 2, QTableWidgetItem(h.get('role', '')))
            date = h.get('date_action')
            self.history_table.setItem(i, 3, QTableWidgetItem(date.strftime('%Y-%m-%d') if date else ''))
            self.history_table.setItem(i, 4, QTableWidgetItem(str(h['_id'])))