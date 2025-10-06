from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QLineEdit,
    QGridLayout, QTableWidget, QTableWidgetItem, QStackedWidget, QFrame, 
    QMessageBox, QHeaderView, QDialog, QMenu, QToolTip
)
from PySide6.QtCore import Qt, QMargins
from PySide6.QtCharts import (
    QChart, QChartView, QPieSeries, QValueAxis, QCategoryAxis, QLineSeries
)
from PySide6.QtGui import QPen, QColor, QPainter, QCursor
from datetime import datetime
from random import randint
from database import (
    get_kpi, get_stock_by_category, get_all_products, delete_product, search_products,
    get_all_suppliers, delete_supplier, search_suppliers,
    get_all_categories, delete_category, search_categories,
    get_all_entries, search_entries,
    get_all_exits, search_exits,
    get_history, search_history,
    get_all_users, delete_user, search_users, get_user
)
from .forms import ProductForm, EntryForm, SupplierForm, CategoryForm, ExitForm, UserForm


class MainWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.user = get_user(self.user_id)
        self.setWindowTitle("Gestion de Stock")
        self.setGeometry(100, 100, 1200, 800)
        
        # Theme global
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6a1b9a, stop:1 #ab47bc);
            }
            QWidget {
                color: white;
            }
            QPushButton {
                background-color: #581c87;
                border: none;
                padding: 10px;
                border-radius: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
            QTableWidget {
                background-color: #312e81;
                gridline-color: #4f46e5;
            }
            QHeaderView::section {
                background-color: #4c1d95;
                color: white;
            }
            QFrame {
                border-radius: 10px;
            }
            QLabel {
                color: white;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top bar
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(20, 10, 20, 10)
        title_label = QLabel("Home")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_bar.addWidget(title_label)
        top_bar.addStretch()
        
        # Profile button with avatar placeholder
        self.profile_btn = QPushButton(f"{self.user['prenom']} {self.user['nom']}")
        self.profile_btn.setStyleSheet("background-color: transparent; border: none;")
        self.profile_btn.clicked.connect(self.show_profile_menu)
        top_bar.addWidget(self.profile_btn)
        
        main_layout.addLayout(top_bar)
        
        # Content layout
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #1e1b4b; border-right: 1px solid #3b0764;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.addWidget(QLabel("<h3>Menu</h3>"))
        
        sections = ['Dashboard', 'Produits', 'Fournisseurs', 'Catégories', 'Utilisateurs', 'Entrées', 'Sorties', 'Historique']
        self.section_buttons = {}
        for section in sections:
            btn = QPushButton(section)
            btn.setStyleSheet("padding: 10px; text-align: left; font-weight: bold; background-color: transparent;")
            btn.clicked.connect(lambda checked, s=section: self.switch_section(s))
            sidebar_layout.addWidget(btn)
            self.section_buttons[section] = btn
        
        sidebar_layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("Déconnexion")
        logout_btn.setStyleSheet("padding: 10px; text-align: left; font-weight: bold; background-color: transparent;")
        logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_btn)
        
        content_layout.addWidget(sidebar)
        
        # Contenu principal
        self.content = QStackedWidget()
        self.content.setStyleSheet("background-color: #1e1b4b;")
        content_layout.addWidget(self.content)
        
        main_layout.addLayout(content_layout)
        
        # Widgets
        self.dashboard_widget = self.create_dashboard()
        self.product_widget = self.create_product_widget()
        self.supplier_widget = self.create_supplier_widget()
        self.category_widget = self.create_category_widget()
        self.user_widget = self.create_user_widget()
        self.entry_widget = self.create_entry_widget()
        self.exit_widget = self.create_exit_widget()
        self.history_widget = self.create_history_widget()
        
        for w in [
            self.dashboard_widget, self.product_widget, self.supplier_widget,
            self.category_widget, self.user_widget, self.entry_widget, 
            self.exit_widget, self.history_widget
        ]:
            self.content.addWidget(w)
        
        self.switch_section('Dashboard')

        # Dict des fonctions de refresh par section
        self.section_refreshers = {
            'Produits': self.load_products,
            'Fournisseurs': self.load_suppliers,
            'Catégories': self.load_categories,
            'Utilisateurs': self.load_users,
            'Entrées': self.load_entries,
            'Sorties': self.load_exits,
            'Historique': self.load_history
        }

    def logout(self):
        self.close()

    def show_profile_menu(self):
        menu = QMenu(self)
        edit_action = menu.addAction("Modifier le profil")
        logout_action = menu.addAction("Déconnexion")
        action = menu.exec_(QCursor.pos())
        if action == edit_action:
            dialog = UserForm(self, self.user, self.user_id)
            dialog.saved.connect(self.update_user_info)
            dialog.exec()
        elif action == logout_action:
            self.logout()

    def update_user_info(self):
        self.user = get_user(self.user_id)
        self.profile_btn.setText(f"{self.user['prenom']} {self.user['nom']}")

    # ============================================================
    # DASHBOARD
    # ============================================================
    def create_dashboard(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # KPI
        kpi = get_kpi()
        kpi_layout = QGridLayout()
        cards = [
            (f"Total Produits\n{kpi['total_prods']}", "#4CAF50"),
            (f"Ruptures Stock\n{kpi['rupture']}", "#F44336"),
            (f"Entrées Récentes\n{kpi['recent_entries']}", "#2196F3"),
            (f"Sorties Récentes\n{kpi['recent_exits']}", "#FF9800")
        ]
        
        for i, (text, color) in enumerate(cards):
            card = QFrame()
            card.setStyleSheet(f"background-color: #1e1b4b; border-radius: 10px; padding: 20px;")
            card_layout = QVBoxLayout(card)
            label = QLabel(text, alignment=Qt.AlignCenter)
            label.setStyleSheet("font-size: 16px; font-weight: bold;")
            card_layout.addWidget(label)
            # Small line chart
            view = self.create_small_chart_view(color)
            card_layout.addWidget(view)
            kpi_layout.addWidget(card, i // 2, i % 2)
        layout.addLayout(kpi_layout)
        
        # Charts
        chart_layout = QHBoxLayout()
        chart_layout.addWidget(QChartView(self.create_line_chart()))
        chart_layout.addWidget(QChartView(self.create_pie_chart()))
        layout.addLayout(chart_layout)
        
        return widget

    def create_small_chart_view(self, color):
        series = QLineSeries()
        for i in range(20):
            series.append(i, randint(1, 10))
        series.setPen(QPen(QColor(color), 2))
        chart = QChart()
        chart.addSeries(series)
        chart.setTheme(QChart.ChartThemeDark)
        chart.legend().hide()
        chart.createDefaultAxes()
        chart.axes(Qt.Horizontal)[0].setVisible(False)
        chart.axes(Qt.Vertical)[0].setVisible(False)
        chart.setMargins(QMargins(0, 0, 0, 0))
        chart.setBackgroundVisible(False)
        view = QChartView(chart)
        view.setFixedHeight(50)
        view.setRenderHint(QPainter.Antialiasing)
        return view

    def create_line_chart(self):
        series = QLineSeries()
        stock_data = get_stock_by_category()
        i = 0
        for value in stock_data.values():
            series.append(i, value)
            i += 1
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Stock global par catégorie")
        chart.setTheme(QChart.ChartThemeDark)
        axisX = QCategoryAxis()
        for j, key in enumerate(stock_data.keys()):
            axisX.append(key, j)
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)
        axisY = QValueAxis()
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)
        return chart

    def create_pie_chart(self):
        kpi = get_kpi()
        series = QPieSeries()
        series.append("Entrées", kpi['recent_entries'])
        series.append("Sorties", kpi['recent_exits'])
        chart = QChart()
        chart.setTitle("Flux de stock récents")
        chart.addSeries(series)
        chart.setTheme(QChart.ChartThemeDark)
        return chart

    # ============================================================
    # FONCTION GÉNÉRIQUE POUR OUVRIR FORMULAIRE ET CONNECTER SIGNAL
    # ============================================================
    def open_form_for_section(self, form_class, section, item_data=None):
        dialog = form_class(self, item_data, self.user_id)
        refresher = self.section_refreshers.get(section)
        if refresher:
            dialog.saved.connect(refresher)
        dialog.exec()

    # ============================================================
    # FONCTIONS UTILITAIRES CRUD + RECHERCHE (générique)
    # ============================================================
    def create_crud_widget(self, table, data_getter, refresher, search_func, form_class, delete_func, headers, columns_map, section, enable_edit=True):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Barre de recherche
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

    # ============================================================
    # PRODUITS
    # ============================================================
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

    # ============================================================
    # FOURNISSEURS
    # ============================================================
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

    # ============================================================
    # CATÉGORIES
    # ============================================================
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

    # ============================================================
    # UTILISATEURS
    # ============================================================
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

    # ============================================================
    # ENTRÉES
    # ============================================================
    def create_entry_widget(self):
        self.entry_table = QTableWidget()
        headers = ['Produit', 'Fournisseur', 'Quantité', 'Prix', 'Date']
        columns_map = {'Produit': 'produit_id', 'Fournisseur': 'fournisseur_id', 'Quantité': 'quantite_entree', 'Prix': 'prix_achat_unitaire', 'Date': 'date_entree'}
        return self.create_crud_widget(self.entry_table, self.load_entries_data, self.load_entries, search_entries, EntryForm, self.delete_entry, headers, columns_map, 'Entrées', enable_edit=False)

    def load_entries_data(self):
        return get_all_entries()

    def load_entries(self):
        entries = self.load_entries_data()
        self.entry_table.setRowCount(len(entries))
        self.entry_table.setColumnCount(6)
        self.entry_table.setHorizontalHeaderLabels(['Produit', 'Fournisseur', 'Quantité', 'Prix', 'Date', 'ID'])
        self.entry_table.setColumnHidden(5, True)
        for i, e in enumerate(entries):
            self.entry_table.setItem(i, 0, QTableWidgetItem(str(e.get('produit_id', ''))))
            self.entry_table.setItem(i, 1, QTableWidgetItem(str(e.get('fournisseur_id', ''))))
            self.entry_table.setItem(i, 2, QTableWidgetItem(str(e.get('quantite_entree', 0))))
            self.entry_table.setItem(i, 3, QTableWidgetItem(str(e.get('prix_achat_unitaire', 0))))
            date = e.get('date_entree')
            self.entry_table.setItem(i, 4, QTableWidgetItem(date.strftime('%Y-%m-%d') if date else ''))
            self.entry_table.setItem(i, 5, QTableWidgetItem(str(e['_id'])))

    def delete_entry(self, entry_id):
        from database import delete_entry
        delete_entry(entry_id)

    # ============================================================
    # SORTIES
    # ============================================================
    def create_exit_widget(self):
        self.exit_table = QTableWidget()
        headers = ['Produit', 'Quantité', 'Date', 'Destination']
        columns_map = {'Produit': 'produit_id', 'Quantité': 'quantite_sortie', 'Date': 'date_sortie', 'Destination': 'destination'}
        return self.create_crud_widget(self.exit_table, self.load_exits_data, self.load_exits, search_exits, ExitForm, self.delete_exit, headers, columns_map, 'Sorties', enable_edit=False)

    def load_exits_data(self):
        return get_all_exits()

    def load_exits(self):
        exits = self.load_exits_data()
        self.exit_table.setRowCount(len(exits))
        self.exit_table.setColumnCount(5)
        self.exit_table.setHorizontalHeaderLabels(['Produit', 'Quantité', 'Date', 'Destination', 'ID'])
        self.exit_table.setColumnHidden(4, True)
        for i, e in enumerate(exits):
            self.exit_table.setItem(i, 0, QTableWidgetItem(str(e.get('produit_id', ''))))
            self.exit_table.setItem(i, 1, QTableWidgetItem(str(e.get('quantite_sortie', 0))))
            date = e.get('date_sortie')
            self.exit_table.setItem(i, 2, QTableWidgetItem(date.strftime('%Y-%m-%d') if date else ''))
            self.exit_table.setItem(i, 3, QTableWidgetItem(e.get('destination', '')))
            self.exit_table.setItem(i, 4, QTableWidgetItem(str(e['_id'])))

    def delete_exit(self, exit_id):
        from database import delete_exit
        delete_exit(exit_id)

    # ============================================================
    # HISTORIQUE
    # ============================================================
    def create_history_widget(self):
        self.history_table = QTableWidget()
        headers = ['Action', 'Produit', 'Utilisateur', 'Date']
        columns_map = {'Action': 'action', 'Produit': 'produit_id', 'Utilisateur': 'utilisateur_id', 'Date': 'date_action'}
        return self.create_crud_widget(self.history_table, self.load_history_data, self.load_history, search_history, UserForm, self.delete_history, headers, columns_map, 'Historique', enable_edit=False)

    def load_history_data(self):
        return get_history()

    def load_history(self):
        history = self.load_history_data()
        self.history_table.setRowCount(len(history))
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(['Action', 'Produit', 'Utilisateur', 'Date', 'ID'])
        self.history_table.setColumnHidden(4, True)
        for i, h in enumerate(history):
            self.history_table.setItem(i, 0, QTableWidgetItem(h.get('action', '')))
            self.history_table.setItem(i, 1, QTableWidgetItem(str(h.get('produit_id', ''))))
            self.history_table.setItem(i, 2, QTableWidgetItem(str(h.get('utilisateur_id', ''))))
            date = h.get('date_action')
            self.history_table.setItem(i, 3, QTableWidgetItem(date.strftime('%Y-%m-%d') if date else ''))
            self.history_table.setItem(i, 4, QTableWidgetItem(str(h['_id'])))

    def delete_history(self, history_id):
        from database import delete_history
        delete_history(history_id)

    # ============================================================
    # NAVIGATION ENTRE LES SECTIONS
    # ============================================================
    def switch_section(self, section):
        for btn in self.section_buttons.values():
            btn.setStyleSheet("padding: 10px; text-align: left; font-weight: bold; background-color: transparent;")
        self.section_buttons[section].setStyleSheet("padding: 10px; text-align: left; font-weight: bold; background-color: #6d28d9;")
        if section == 'Dashboard':
            self.content.setCurrentWidget(self.dashboard_widget)
        elif section == 'Produits':
            self.content.setCurrentWidget(self.product_widget)
            self.load_products()
        elif section == 'Fournisseurs':
            self.content.setCurrentWidget(self.supplier_widget)
            self.load_suppliers()
        elif section == 'Catégories':
            self.content.setCurrentWidget(self.category_widget)
            self.load_categories()
        elif section == 'Utilisateurs':
            self.content.setCurrentWidget(self.user_widget)
            self.load_users()
        elif section == 'Entrées':
            self.content.setCurrentWidget(self.entry_widget)
            self.load_entries()
        elif section == 'Sorties':
            self.content.setCurrentWidget(self.exit_widget)
            self.load_exits()
        elif section == 'Historique':
            self.content.setCurrentWidget(self.history_widget)
            self.load_history()