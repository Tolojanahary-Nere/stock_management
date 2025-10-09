from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from database import get_all_suppliers, delete_supplier, search_suppliers
from .forms import SupplierForm

class SuppliersMixin:
    def create_supplier_widget(self):
        self.supplier_table = QTableWidget()
        headers = ['Nom', 'Contact', 'Email', 'Adresse']
        columns_map = {'Nom': 'nom_fournisseur', 'Contact': 'contact', 'Email': 'email', 'Adresse': 'adresse'}
        return self.create_crud_widget(self.supplier_table, self.load_suppliers_data, self.load_suppliers, search_suppliers, SupplierForm, delete_supplier, headers, columns_map, 'Fournisseurs')

    def load_suppliers_data(self):
        return get_all_suppliers()

    def load_suppliers(self):
        suppliers = self.load_suppliers_data()
        self.supplier_table.setRowCount(len(suppliers))
        self.supplier_table.setColumnCount(5)
        self.supplier_table.setHorizontalHeaderLabels(['Nom', 'Contact', 'Email', 'Adresse', 'ID'])
        self.supplier_table.setColumnHidden(4, True)
        for i, s in enumerate(suppliers):
            self.supplier_table.setItem(i, 0, QTableWidgetItem(s.get('nom_fournisseur', '')))
            self.supplier_table.setItem(i, 1, QTableWidgetItem(s.get('contact', '')))
            self.supplier_table.setItem(i, 2, QTableWidgetItem(s.get('email', '')))
            self.supplier_table.setItem(i, 3, QTableWidgetItem(s.get('adresse', '')))
            self.supplier_table.setItem(i, 4, QTableWidgetItem(str(s['_id'])))