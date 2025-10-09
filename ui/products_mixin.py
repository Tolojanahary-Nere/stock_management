from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from database import get_all_products, delete_product, search_products
from .forms import ProductForm

class ProductsMixin:
    def create_product_widget(self):
        self.product_table = QTableWidget()
        headers = ['Nom', 'Référence', 'Catégorie', 'Fournisseur', 'Quantité', 'Prix']
        columns_map = {'Nom': 'nom', 'Référence': 'reference', 'Catégorie': 'categorie', 
                       'Fournisseur': 'fournisseur', 'Quantité': 'quantite_stock', 'Prix': 'prix_unitaire'}
        return self.create_crud_widget(self.product_table, self.load_products_data, self.load_products, search_products, ProductForm, delete_product, headers, columns_map, 'Produits')

    def load_products_data(self):
        return get_all_products()

    def load_products(self):
        products = self.load_products_data()
        self.product_table.setRowCount(len(products))
        self.product_table.setColumnCount(7)
        self.product_table.setHorizontalHeaderLabels(['Nom', 'Référence', 'Catégorie', 'Fournisseur', 'Quantité', 'Prix', 'ID'])
        self.product_table.setColumnHidden(6, True)
        for i, prod in enumerate(products):
            self.product_table.setItem(i, 0, QTableWidgetItem(prod.get('nom', '')))
            self.product_table.setItem(i, 1, QTableWidgetItem(prod.get('reference', '')))
            self.product_table.setItem(i, 2, QTableWidgetItem(prod.get('categorie', '')))
            self.product_table.setItem(i, 3, QTableWidgetItem(prod.get('fournisseur', '')))
            self.product_table.setItem(i, 4, QTableWidgetItem(str(prod.get('quantite_stock', 0))))
            self.product_table.setItem(i, 5, QTableWidgetItem(str(prod.get('prix_unitaire', 0))))
            self.product_table.setItem(i, 6, QTableWidgetItem(str(prod['_id'])))