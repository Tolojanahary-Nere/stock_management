from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
from datetime import datetime
from bson import ObjectId
from database import DB

class CrudMixin:
    def open_form_for_section(self, form_class, section, item_data=None):
        dialog = form_class(self, item_data, self.user_id)
        refresher = self.section_refreshers.get(section)
        if refresher:
            dialog.saved.connect(refresher)
        dialog.exec()

    def create_crud_widget(self, table, data_getter, refresher, search_func, form_class, delete_func, headers, columns_map, section, enable_edit=True):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Barre de recherche moderne
        search_layout = QHBoxLayout()
        search_label = QLabel("Recherche :")
        search_input = QLineEdit()
        search_input.setPlaceholderText("Tapez pour filtrer...")
        search_input.textChanged.connect(lambda text: self.filter_table(table, search_func, text, columns_map))
        search_layout.addWidget(search_label)
        search_layout.addWidget(search_input)
        layout.addLayout(search_layout)
        
        # Boutons CRUD
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        add_btn = QPushButton("Ajouter")
        add_btn.clicked.connect(lambda: self.open_form_for_section(form_class, section))
        btn_layout.addWidget(add_btn)
        
        if enable_edit:
            edit_btn = QPushButton("Modifier")
            edit_btn.clicked.connect(lambda: self.edit_item(table, data_getter, form_class, section))
            btn_layout.addWidget(edit_btn)
        
        del_btn = QPushButton("Supprimer")
        del_btn.clicked.connect(lambda: self.delete_item(table, delete_func, refresher))
        btn_layout.addWidget(del_btn)
        
        layout.addLayout(btn_layout)
        
        # Tableau
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(table)
        
        refresher()  # Charge initial
        return widget

    def filter_table(self, table, search_func, query, columns_map):
        data = search_func(query) if query else search_func('')
        data = self.enrich_data(data, columns_map)  # Enrich if needed
        table.setRowCount(len(data))
        if data:
            num_cols = len(columns_map)
            table.setColumnCount(num_cols + 1)
            table.setHorizontalHeaderLabels(list(columns_map.keys()) + ['ID'])
            table.setColumnHidden(num_cols, True)
            for i, item in enumerate(data):
                for col_idx, (header, key) in enumerate(columns_map.items()):
                    value = item.get(key, '')
                    if isinstance(value, datetime):
                        value = value.strftime('%Y-%m-%d')
                    table.setItem(i, col_idx, QTableWidgetItem(str(value)))
                table.setItem(i, num_cols, QTableWidgetItem(str(item['_id'])))
            table.resizeColumnsToContents()

    def enrich_data(self, data, columns_map):
        if 'produit_nom' in columns_map.values() or 'role' in columns_map.values():
            for h in data:
                if 'produit_id' in h and h.get('produit_id'):
                    prod = DB['produits'].find_one({'_id': ObjectId(h['produit_id'])})
                    h['produit_nom'] = prod['nom'] if prod else ''
                else:
                    h['produit_nom'] = ''
                if 'utilisateur_id' in h and h.get('utilisateur_id'):
                    user = DB['utilisateurs'].find_one({'_id': ObjectId(h['utilisateur_id'])})
                    h['role'] = user['role'] if user else ''
                else:
                    h['role'] = ''
                if 'fournisseur_id' in h and h.get('fournisseur_id'):
                    fourn = DB['fournisseurs'].find_one({'_id': ObjectId(h['fournisseur_id'])})
                    h['fournisseur_nom'] = fourn['nom_fournisseur'] if fourn else ''
                else:
                    h['fournisseur_nom'] = ''
        return data

    def edit_item(self, table, data_getter, form_class, section):
        selected = table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une ligne à modifier")
            return
        row = selected[0].row()
        id_col = table.columnCount() - 1
        item_id = table.item(row, id_col).text()
        item_data = next((item for item in data_getter() if str(item['_id']) == item_id), None)
        if not item_data:
            QMessageBox.warning(self, "Erreur", "Élément non trouvé")
            return
        self.open_form_for_section(form_class, section, item_data)

    def delete_item(self, table, delete_func, refresher):
        selected = table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une ligne à supprimer")
            return
        row = selected[0].row()
        id_col = table.columnCount() - 1
        item_id = table.item(row, id_col).text()
        if QMessageBox.question(self, "Confirmation", "Supprimer cet élément ?") == QMessageBox.Yes:
            delete_func(str(item_id))
            refresher()
            self.refresh_dashboard()  # Refresh dashboard after deletion