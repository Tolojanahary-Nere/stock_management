from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from datetime import datetime
from database import get_all_exits, delete_exit, search_exits
from .forms import ExitForm

class ExitsMixin:
    def create_exit_widget(self):
        self.exit_table = QTableWidget()
        headers = ['Produit', 'Quantité', 'Date', 'Destination']
        columns_map = {'Produit': 'produit_nom', 'Quantité': 'quantite_sortie', 'Date': 'date_sortie', 'Destination': 'destination'}
        return self.create_crud_widget(self.exit_table, self.load_exits_data, self.load_exits, search_exits, ExitForm, delete_exit, headers, columns_map, 'Sorties', enable_edit=False)

    def load_exits_data(self):
        return get_all_exits()

    def load_exits(self):
        exits = self.load_exits_data()
        exits = self.enrich_data(exits, {'Produit': 'produit_nom'})
        self.exit_table.setRowCount(len(exits))
        self.exit_table.setColumnCount(5)
        self.exit_table.setHorizontalHeaderLabels(['Produit', 'Quantité', 'Date', 'Destination', 'ID'])
        self.exit_table.setColumnHidden(4, True)
        for i, e in enumerate(exits):
            self.exit_table.setItem(i, 0, QTableWidgetItem(e.get('produit_nom', 'Inconnu')))
            self.exit_table.setItem(i, 1, QTableWidgetItem(str(e.get('quantite_sortie', 0))))
            date = e.get('date_sortie')
            self.exit_table.setItem(i, 2, QTableWidgetItem(date.strftime('%Y-%m-%d') if date else ''))
            self.exit_table.setItem(i, 3, QTableWidgetItem(e.get('destination', '')))
            self.exit_table.setItem(i, 4, QTableWidgetItem(str(e['_id'])))