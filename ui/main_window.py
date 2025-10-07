from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QLineEdit,
    QGridLayout, QTableWidget, QTableWidgetItem, QStackedWidget, QFrame, 
    QMessageBox, QHeaderView, QDialog, QMenu, QToolTip, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QCalendarWidget
)
from PySide6.QtCore import Qt, QMargins, QRectF
from PySide6.QtCharts import (
    QChart, QChartView, QPieSeries, QValueAxis, QCategoryAxis, QLineSeries
)
from PySide6.QtGui import QPen, QColor, QPainter, QCursor, QFont, QBrush
from datetime import datetime
from random import randint
from bson import ObjectId
from database import (
    get_kpi, get_stock_by_category, get_all_products, delete_product, search_products,
    get_all_suppliers, delete_supplier, search_suppliers,
    get_all_categories, delete_category, search_categories,
    get_all_entries, search_entries, delete_entry,
    get_all_exits, search_exits, delete_exit,
    get_history, search_history, delete_history,
    get_all_users, delete_user, search_users, get_user, DB
)
from .forms import ProductForm, EntryForm, SupplierForm, CategoryForm, ExitForm, UserForm


class MainWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.user = get_user(self.user_id)
        self.setWindowTitle("Gestion de Stock")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        
        self.theme = 'dark'
        self.dark_style = """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1e3c72, stop:1 #2a5298);
            }
            QWidget {
                color: white;
                font-family: Arial, sans-serif;
            }
            QPushButton {
                background-color: #3498db;
                border: none;
                padding: 12px;
                border-radius: 8px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QTableWidget {
                background-color: #34495e;
                gridline-color: #bdc3c7;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
            }
            QFrame {
                border-radius: 10px;
                background-color: rgba(255,255,255,0.1);
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
            QComboBox {
                background-color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
            QCalendarWidget {
                background-color: #34495e;
                color: white;
            }
        """
        self.light_style = """
            QMainWindow {
                background: white;
            }
            QWidget {
                color: black;
                font-family: Arial, sans-serif;
            }
            QPushButton {
                background-color: #3498db;
                border: none;
                padding: 12px;
                border-radius: 8px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QTableWidget {
                background-color: #f0f0f0;
                gridline-color: #bdc3c7;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                color: black;
                padding: 8px;
                border: none;
            }
            QFrame {
                border-radius: 10px;
                background-color: rgba(0,0,0,0.05);
            }
            QLabel {
                color: black;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #f0f0f0;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                color: black;
            }
            QComboBox {
                background-color: #f0f0f0;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                color: black;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: #f0f0f0;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                color: black;
            }
            QCalendarWidget {
                background-color: #f0f0f0;
                color: black;
            }
        """
        self.setStyleSheet(self.dark_style)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Top bar moderne
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(20, 15, 20, 15)
        title_label = QLabel("Home")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        top_bar.addWidget(title_label)
        top_bar.addStretch()
        
        # Profile avec avatar
        profile_layout = QHBoxLayout()
        self.avatar_view = QGraphicsView()
        self.avatar_view.setFixedSize(40, 40)
        self.avatar_view.setStyleSheet("background: transparent; border: none;")
        self.avatar_scene = QGraphicsScene()
        self.ellipse = QGraphicsEllipseItem(QRectF(0, 0, 40, 40))
        self.ellipse.setBrush(QBrush(QColor("#3498db")))
        self.avatar_scene.addItem(self.ellipse)
        initial_text = QGraphicsTextItem(f"{self.user['prenom'][0]}{self.user['nom'][0]}")
        initial_text.setFont(QFont("Arial", 14, QFont.Bold))
        initial_text.setDefaultTextColor(QColor("white"))
        initial_text.setPos(8, 8)
        self.avatar_scene.addItem(initial_text)
        self.avatar_view.setScene(self.avatar_scene)
        profile_layout.addWidget(self.avatar_view)
        
        self.profile_btn = QPushButton(f"{self.user['prenom']} {self.user['nom']}")
        self.profile_btn.setStyleSheet("background-color: transparent; border: none; font-size: 14px;")
        self.profile_btn.clicked.connect(self.show_profile_menu)
        profile_layout.addWidget(self.profile_btn)
        
        top_bar.addLayout(profile_layout)
        
        self.main_layout.addLayout(top_bar)
        
        # Content layout
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Sidebar moderne
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("background-color: #2c3e50; border-right: 1px solid #34495e;" if self.theme == 'dark' else "background-color: #f0f0f0; border-right: 1px solid #e0e0e0;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.addWidget(QLabel("<h3 style='color: #ecf0f1;'>Menu</h3>" if self.theme == 'dark' else "<h3 style='color: #2c3e50;'>Menu</h3>"))
        
        sections = ['Dashboard', 'Produits', 'Fournisseurs', 'Catégories', 'Utilisateurs', 'Entrées', 'Sorties', 'Historique']
        self.section_buttons = {}
        for section in sections:
            btn = QPushButton(section)
            btn.setStyleSheet("padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #bdc3c7;" if self.theme == 'dark' else "padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #2c3e50;")
            btn.clicked.connect(lambda checked, s=section: self.switch_section(s))
            sidebar_layout.addWidget(btn)
            self.section_buttons[section] = btn
        
        sidebar_layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("Déconnexion")
        logout_btn.setStyleSheet("padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #e74c3c;")
        logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_btn)
        
        content_layout.addWidget(self.sidebar)
        
        # Contenu principal
        self.content = QStackedWidget()
        self.content.setStyleSheet("background-color: #34495e;" if self.theme == 'dark' else "background-color: #f0f0f0;")
        content_layout.addWidget(self.content)
        
        self.main_layout.addLayout(content_layout)
        
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

    def switch_theme(self):
        if self.theme == 'dark':
            self.setStyleSheet(self.light_style)
            self.theme = 'light'
            self.sidebar.setStyleSheet("background-color: #f0f0f0; border-right: 1px solid #e0e0e0;")
            for btn in self.section_buttons.values():
                btn.setStyleSheet("padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #2c3e50;")
            self.content.setStyleSheet("background-color: #f0f0f0;")
        else:
            self.setStyleSheet(self.dark_style)
            self.theme = 'dark'
            self.sidebar.setStyleSheet("background-color: #2c3e50; border-right: 1px solid #34495e;")
            for btn in self.section_buttons.values():
                btn.setStyleSheet("padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #bdc3c7;")
            self.content.setStyleSheet("background-color: #34495e;")
        self.refresh_dashboard()

    def logout(self):
        self.close()

    def show_profile_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
            }
            QMenu::item:selected {
                background-color: #3498db;
            }
        """ if self.theme == 'dark' else """
            QMenu {
                background-color: #f0f0f0;
                color: black;
                border: 1px solid #e0e0e0;
            }
            QMenu::item:selected {
                background-color: #3498db;
            }
        """)
        edit_action = menu.addAction("Modifier le profil")
        theme_action = menu.addAction("Changer thème")
        logout_action = menu.addAction("Déconnexion")
        action = menu.exec_(QCursor.pos())
        if action == edit_action:
            dialog = UserForm(self, self.user, self.user_id)
            dialog.saved.connect(self.update_user_info)
            dialog.exec()
        elif action == theme_action:
            self.switch_theme()
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
        layout.setContentsMargins(30, 30, 30, 30)
        
        greeting = QLabel(f"Bonjour, {self.user['prenom']} bienvenue!")
        greeting.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(greeting)
        
        # KPI moderne
        kpi = get_kpi()
        kpi_layout = QGridLayout()
        kpi_layout.setSpacing(20)
        cards = [
            (f"Total Produits\n{kpi['total_prods']}", "#3498db"),
            (f"Ruptures Stock\n{kpi['rupture']}", "#e74c3c"),
            (f"Entrées Récentes\n{kpi['recent_entries']}", "#2ecc71"),
            (f"Sorties Récentes\n{kpi['recent_exits']}", "#f39c12")
        ]
        
        for i, (text, color) in enumerate(cards):
            card = QFrame()
            card.setStyleSheet(f"background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px;" if self.theme == 'dark' else f"background-color: rgba(0,0,0,0.05); border-radius: 12px; padding: 20px;")
            card_layout = QVBoxLayout(card)
            label = QLabel(text, alignment=Qt.AlignCenter)
            label.setStyleSheet("font-size: 18px; font-weight: bold;")
            card_layout.addWidget(label)
            # Small line chart
            view = self.create_small_chart_view(color)
            card_layout.addWidget(view)
            kpi_layout.addWidget(card, i // 2, i % 2)
        layout.addLayout(kpi_layout)
        
        # Charts and calendar
        chart_cal_layout = QHBoxLayout()
        line_view = QChartView(self.create_line_chart())
        line_view.setStyleSheet("background: transparent;")
        chart_cal_layout.addWidget(line_view, stretch=2)
        
        cal = QCalendarWidget()
        chart_cal_layout.addWidget(cal, stretch=1)
        
        layout.addLayout(chart_cal_layout)
        
        # Recent movements
        recent_label = QLabel("Derniers mouvements")
        recent_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(recent_label)
        
        recent_table = QTableWidget()
        recent_table.setColumnCount(4)
        recent_table.setHorizontalHeaderLabels(['Type', 'Produit', 'Quantité', 'Date'])
        recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        entries = get_all_entries()
        exits = get_all_exits()
        movements = []
        for e in entries:
            e['type'] = 'Entrée'
            e['quantite'] = e['quantite_entree']
            e['date'] = e['date_entree']
            movements.append(e)
        for s in exits:
            s['type'] = 'Sortie'
            s['quantite'] = s['quantite_sortie']
            s['date'] = s['date_sortie']
            movements.append(s)
        movements.sort(key=lambda m: m['date'], reverse=True)
        movements = movements[:5]
        
        recent_table.setRowCount(len(movements))
        for i, m in enumerate(movements):
            product = DB['produits'].find_one({'_id': ObjectId(m['produit_id'])}) or {}
            nom = product.get('nom', 'Inconnu')
            recent_table.setItem(i, 0, QTableWidgetItem(m['type']))
            recent_table.setItem(i, 1, QTableWidgetItem(nom))
            recent_table.setItem(i, 2, QTableWidgetItem(str(m['quantite'])))
            recent_table.setItem(i, 3, QTableWidgetItem(m['date'].strftime('%Y-%m-%d')))
        
        layout.addWidget(recent_table)
        
        return widget
    
    def refresh_dashboard(self):
        """Recharge les données du tableau de bord (KPI et graphiques)"""
        self.content.removeWidget(self.dashboard_widget)
        self.dashboard_widget.deleteLater()
        self.dashboard_widget = self.create_dashboard()
        self.content.insertWidget(0, self.dashboard_widget)
        if self.content.currentWidget() == self.dashboard_widget or self.section_buttons['Dashboard'].styleSheet().find('#3498db') != -1:
            self.content.setCurrentWidget(self.dashboard_widget)

    def create_small_chart_view(self, color):
        series = QLineSeries()
        for i in range(20):
            series.append(i, randint(1, 10))
        series.setPen(QPen(QColor(color), 2))
        chart = QChart()
        chart.addSeries(series)
        chart.setTheme(QChart.ChartThemeDark if self.theme == 'dark' else QChart.ChartThemeLight)
        chart.legend().hide()
        chart.createDefaultAxes()
        chart.axes(Qt.Horizontal)[0].setVisible(False)
        chart.axes(Qt.Vertical)[0].setVisible(False)
        chart.setMargins(QMargins(0, 0, 0, 0))
        chart.setBackgroundVisible(False)
        view = QChartView(chart)
        view.setFixedHeight(60)
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
        chart.setTitleBrush(QBrush(QColor("white" if self.theme == 'dark' else "black")))
        chart.setTheme(QChart.ChartThemeDark if self.theme == 'dark' else QChart.ChartThemeLight)
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
        chart.setTitleBrush(QBrush(QColor("white" if self.theme == 'dark' else "black")))
        chart.addSeries(series)
        chart.setTheme(QChart.ChartThemeDark if self.theme == 'dark' else QChart.ChartThemeLight)
        return chart

    def check_low_stock(self):
        low = [p for p in get_all_products() if p['quantite_stock'] < 50]
        if low:
            names = ", ".join(p['nom'] for p in low)
            QMessageBox.warning(self, "Alerte Stock Bas", f"Les produits suivants ont un stock bas (<50): {names}")

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

    # ============================================================
    # SORTIES
    # ============================================================
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

    # ============================================================
    # HISTORIQUE
    # ============================================================
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

    # ============================================================
    # NAVIGATION ENTRE LES SECTIONS
    # ============================================================
    def switch_section(self, section):
        for btn in self.section_buttons.values():
            btn.setStyleSheet("padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #bdc3c7;" if self.theme == 'dark' else "padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #2c3e50;")
        self.section_buttons[section].setStyleSheet("padding: 12px; text-align: left; font-weight: bold; background-color: #3498db; color: white;")
        if section == 'Dashboard':
            self.content.setCurrentWidget(self.dashboard_widget)
            self.check_low_stock()
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