from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from database import get_all_categories, delete_category, search_categories
from .forms import CategoryForm

class CategoriesMixin:
    def create_category_widget(self):
        self.category_table = QTableWidget()
        headers = ['Nom', 'Description']
        columns_map = {'Nom': 'nom_categorie', 'Description': 'description'}
        return self.create_crud_widget(self.category_table, self.load_categories_data, self.load_categories, search_categories, CategoryForm, delete_category, headers, columns_map, 'Catégories')

    def load_categories_data(self):
        return get_all_categories()

    def load_categories(self):
        cats = self.load_categories_data()
        self.category_table.setRowCount(len(cats))
        self.category_table.setColumnCount(3)
        self.category_table.setHorizontalHeaderLabels(['Nom', 'Description', 'ID'])
        self.category_table.setColumnHidden(2, True)
        for i, c in enumerate(cats):
            self.category_table.setItem(i, 0, QTableWidgetItem(c.get('nom_categorie', '')))
            self.category_table.setItem(i, 1, QTableWidgetItem(c.get('description', '')))
            self.category_table.setItem(i, 2, QTableWidgetItem(str(c['_id'])))