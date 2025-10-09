from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from datetime import datetime
from database import get_all_entries, delete_entry, search_entries
from .forms import EntryForm

class EntriesMixin:
    def create_entry_widget(self):
        self.entry_table = QTableWidget()
        headers = ['Produit', 'Fournisseur', 'Quantité', 'Prix', 'Date']
        columns_map = {'Produit': 'produit_nom', 'Fournisseur': 'fournisseur_nom', 'Quantité': 'quantite_entree', 'Prix': 'prix_achat_unitaire', 'Date': 'date_entree'}
        return self.create_crud_widget(self.entry_table, self.load_entries_data, self.load_entries, search_entries, EntryForm, delete_entry, headers, columns_map, 'Entrées', enable_edit=False)

    def load_entries_data(self):
        return get_all_entries()

    def load_entries(self):
        entries = self.load_entries_data()
        entries = self.enrich_data(entries, {'Produit': 'produit_nom', 'Fournisseur': 'fournisseur_nom'})
        self.entry_table.setRowCount(len(entries))
        self.entry_table.setColumnCount(6)
        self.entry_table.setHorizontalHeaderLabels(['Produit', 'Fournisseur', 'Quantité', 'Prix', 'Date', 'ID'])
        self.entry_table.setColumnHidden(5, True)
        for i, e in enumerate(entries):
            self.entry_table.setItem(i, 0, QTableWidgetItem(e.get('produit_nom', 'Inconnu')))
            self.entry_table.setItem(i, 1, QTableWidgetItem(e.get('fournisseur_nom', 'Inconnu')))
            self.entry_table.setItem(i, 2, QTableWidgetItem(str(e.get('quantite_entree', 0))))
            self.entry_table.setItem(i, 3, QTableWidgetItem(str(e.get('prix_achat_unitaire', 0))))
            date = e.get('date_entree')
            self.entry_table.setItem(i, 4, QTableWidgetItem(date.strftime('%Y-%m-%d') if date else ''))
            self.entry_table.setItem(i, 5, QTableWidgetItem(str(e['_id'])))