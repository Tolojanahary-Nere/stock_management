# main_window.py updated with custom notification popup
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel,
    QStackedWidget, QFrame, QMenu, QMessageBox, QToolButton, QWidgetAction
)
from PySide6.QtCore import Qt, QPoint, QSize
from PySide6.QtGui import QColor, QCursor, QFont, QBrush, QIcon, QPixmap, QPainter
from database import get_user, get_all_products
from .forms import UserForm
from .dashboard_mixin import DashboardMixin
from .crud_mixin import CrudMixin
from .products_mixin import ProductsMixin
from .suppliers_mixin import SuppliersMixin
from .categories_mixin import CategoriesMixin
from .users_mixin import UsersMixin
from .entries_mixin import EntriesMixin
from .exits_mixin import ExitsMixin
from .history_mixin import HistoryMixin

class MainWindow(QMainWindow, DashboardMixin, CrudMixin, ProductsMixin, SuppliersMixin, CategoriesMixin, UsersMixin, EntriesMixin, ExitsMixin, HistoryMixin):
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
    background-color: #0a0f1c;
}
QWidget {
    color: #e6e6e6;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QPushButton {
    background-color: #5a8dee;
    border: none;
    padding: 12px;
    border-radius: 20px;
    color: #e6e6e6;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #1a2742;
    color: #e6e6e6;
}
QTableWidget {
    background-color: #111a2d;
    gridline-color: #2c3b55;
    border-radius: 12px;
}
QHeaderView::section {
    background-color: #111a2d;
    color: #e6e6e6;
    padding: 8px;
    border: none;
    border-radius: 12px;
    font-weight: bold;
}
QFrame {
    border-radius: 12px;
    background-color: rgba(255,255,255,0.04);
}
QLabel {
    color: #e6e6e6;
    font-size: 14px;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #111a2d;
    border: 1px solid #2c3b55;
    border-radius: 8px;
    padding: 8px;
    color: #e6e6e6;
}
QCalendarWidget {
    background-color: #111a2d;
    color: #e6e6e6;
    selection-background-color: #5a8dee;
}
QToolButton {
    background: transparent;
    border: none;
    color: #e6e6e6;
}
QToolButton:hover {
    background: rgba(26, 39, 66, 0.5);
    border-radius: 6px;
}
QToolButton#notificationButton, 
QToolButton#avatarButton, 
QToolButton#searchButton {
    color: #5a8dee;
    font-weight: bold;
}
QMenu {
    background-color: #0a0f1c;
    color: #e6e6e6;
    border: 1px solid #2c3b55;
    border-radius: 8px;
}
QMenu::item:selected {
    background-color: #5a8dee;
}
QLabel#badgeLabel {
    background-color: red;
    color: white;
    border-radius: 8px;
    padding: 2px 6px;
    font-size: 10px;
}
"""
        self.light_style = """
    QMainWindow {
        background: #f9f9f9;
    }
    QWidget {
        color: #021526;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    QPushButton {
        background-color: #6eacda; /* Bleu clair */
        border: none;
        padding: 12px;
        border-radius: 10px;
        color: white;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #03346e; /* Bleu foncé au hover */
    }
    QTableWidget {
        background-color: #ffffff;
        gridline-color: #e0e0e0;
        border-radius: 8px;
    }
    QHeaderView::section {
        background-color: #e2e2b6;
        color: #021526;
        padding: 8px;
        border: none;
        font-weight: bold;
    }
    QFrame {
        border-radius: 10px;
        background-color: rgba(0, 0, 0, 0.03);
    }
    QLabel {
        color: #021526;
        font-size: 14px;
    }
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
        background-color: #e2e2b6;
        border: 1px solid #6eacda;
        border-radius: 8px;
        padding: 8px;
        color: #021526;
    }
    QCalendarWidget {
        background-color: #ffffff;
        color: #021526;
        selection-background-color: #03346e;
    }
    QToolButton {
        background: transparent;
        border: none;
    }
    QToolButton:hover {
        background: rgba(3, 52, 110, 0.1);
        border-radius: 6px;
    }

    /* === Icônes du topbar === */
    QToolButton#notificationButton, 
    QToolButton#avatarButton, 
    QToolButton#searchButton {
        color: #03346e; /* bleu foncé */
        font-weight: bold;
    }

    QLabel#badgeLabel {
        background-color: red;
        color: white;
        border-radius: 8px;
        padding: 2px 6px;
        font-size: 10px;
    }
QMenu {
    background-color: #f9f9f9;
    color: #021526;
    border: 1px solid #6eacda;
    border-radius: 8px;
}
QMenu::item:selected {
    background-color: #03346e;
    color: white;
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
        top_bar.setSpacing(20)
        
        # Logo
        self.logo_label = QLabel("Stockly")
        self.logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        top_bar.addWidget(self.logo_label)
        
        self.title_label = QLabel("Home")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-left: 20px; color: white;")
        top_bar.addWidget(self.title_label)
        top_bar.addStretch()
        
        # Recherche
        self.search_btn = QToolButton()
        self.search_btn.setObjectName("searchButton")
        self.search_btn.setIcon(QIcon.fromTheme("system-search"))
        self.search_btn.setIconSize(QSize(28, 28))
        self.search_btn.clicked.connect(self.show_search)
        top_bar.addWidget(self.search_btn)
        
        # Cloche de notifications avec badge
        notification_container = QWidget()
        notification_layout = QHBoxLayout(notification_container)
        notification_layout.setContentsMargins(0, 0, 0, 0)
        self.notification_btn = QToolButton()
        self.notification_btn.setObjectName("notificationButton")
        self.notification_btn.setIcon(QIcon("./assets/icons/bell.jpeg"))
        self.notification_btn.setIconSize(QSize(28, 28))
        self.notification_btn.clicked.connect(self.show_notifications)
        notification_layout.addWidget(self.notification_btn)
        
        self.notification_badge = QLabel()
        self.notification_badge.setObjectName("badgeLabel")
        self.notification_badge.setStyleSheet("""
            background-color: red;
            color: white;
            border-radius: 6px;
            padding: 1px 4px;
            font-size: 8px;
            font-weight: bold;
        """)
        self.notification_badge.setVisible(False)
        # Position badge on top-right of bell
        self.notification_badge.setParent(self.notification_btn)
        self.notification_badge.move(15, -2)  # Adjust position
        top_bar.addWidget(notification_container)
        
        # Profile avec avatar et flèche
        self.profile_btn = QToolButton()
        self.profile_btn.setObjectName("avatarButton")
        self.profile_btn.setText(f"{self.user['prenom']} {self.user['nom']} ▼")
        self.profile_btn.setStyleSheet("background-color: transparent; border: none; font-size: 14px; color: white;")
        self.profile_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.profile_btn.setIconSize(QSize(28, 28))
        
        # Create avatar directly with QPixmap (no QGraphicsView/Scene)
        avatar_pixmap = QPixmap(36, 36)
        avatar_pixmap.fill(Qt.transparent)
        painter = QPainter(avatar_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor("#6eacda")))  # fond bleu clair
        painter.setPen(QColor("#03346e"))  # bordure bleu foncé
        painter.drawEllipse(1, 1, 34, 34)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
        initial = f"{self.user['prenom'][0]}{self.user['nom'][0]}"
        painter.drawText(avatar_pixmap.rect(), Qt.AlignCenter, initial)
        painter.end()
        self.profile_btn.setIcon(QIcon(avatar_pixmap))
        self.profile_btn.clicked.connect(self.show_profile_menu)
        top_bar.addWidget(self.profile_btn)
        
        self.main_layout.addLayout(top_bar)
        
        # Content layout
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Sidebar moderne
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("background-color: #111a2d; border-right: 1px solid #2c3b55;" if self.theme == 'dark' else "background-color: #f9f9f9; border-right: 1px solid #e0e0e0;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        self.menu_label = QLabel("<h3 style='color: #ffffff;'>Menu</h3>")
        sidebar_layout.addWidget(self.menu_label)
        
        sections = [
            ('Dashboard', 'user-home'),
            ('Produits', 'folder'),
            ('Fournisseurs', 'system-users'),
            ('Catégories', 'folder'),
            ('Utilisateurs', 'system-users'),
            ('Entrées', 'go-up'),
            ('Sorties', 'go-down'),
            ('Historique', 'document-open-recent')
        ]
        self.section_buttons = {}
        for section, icon_name in sections:
            btn = QPushButton(section)
            btn.setIcon(QIcon.fromTheme(icon_name))
            btn.setStyleSheet("padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #e6e6e6; border-radius: 20px;" if self.theme == 'dark' else "padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #021526; border-radius: 20px;")
            btn.clicked.connect(lambda checked, s=section: self.switch_section(s))
            sidebar_layout.addWidget(btn)
            self.section_buttons[section] = btn
        
        sidebar_layout.addStretch()
        
        # Help button
        self.help_btn = QPushButton("? Help")
        self.help_btn.setIcon(QIcon.fromTheme("help-contents"))
        self.help_btn.setStyleSheet("padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #e6e6e6; border-radius: 20px;" if self.theme == 'dark' else "padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #021526; border-radius: 20px;")
        self.help_btn.clicked.connect(self.show_help)
        sidebar_layout.addWidget(self.help_btn)
        
        # Logout button
        self.logout_btn = QPushButton("Log Out")
        self.logout_btn.setIcon(QIcon.fromTheme("system-log-out"))
        self.logout_btn.setStyleSheet("padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #ef5350; border-radius: 20px;")
        self.logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(self.logout_btn)
        
        content_layout.addWidget(self.sidebar)
        
        # Contenu principal
        self.content = QStackedWidget()
        self.content.setStyleSheet("background-color: #0a0f1c;" if self.theme == 'dark' else "background-color: #f9f9f9;")
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
        self.update_notification_count()

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

        self.switch_theme()

    def switch_theme(self):
        if self.theme == 'dark':
            self.setStyleSheet(self.light_style)
            self.theme = 'light'
            self.sidebar.setStyleSheet("background-color: #f9f9f9; border-right: 1px solid #e0e0e0;")
            self.content.setStyleSheet("background-color: #f9f9f9;")
            self.menu_label.setText("<h3 style='color: #021526;'>Menu</h3>")
            self.logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #021526;")
            self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-left: 20px; color: #021526;")
            self.profile_btn.setStyleSheet("background-color: transparent; border: none; font-size: 14px; color: #021526;")
            btn_style = "padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #021526; border-radius: 20px;"
            for btn in list(self.section_buttons.values()) + [self.help_btn]:
                btn.setStyleSheet(btn_style)
            self.logout_btn.setStyleSheet("padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #ef5350; border-radius: 20px;")
        else:
            self.setStyleSheet(self.dark_style)
            self.theme = 'dark'
            self.sidebar.setStyleSheet("background-color: #111a2d; border-right: 1px solid #2c3b55;")
            self.content.setStyleSheet("background-color: #0a0f1c;")
            self.menu_label.setText("<h3 style='color: #e6e6e6;'>Menu</h3>")
            self.logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #e6e6e6;")
            self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-left: 20px; color: #e6e6e6;")
            self.profile_btn.setStyleSheet("background-color: transparent; border: none; font-size: 14px; color: #e6e6e6;")
            btn_style = "padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #e6e6e6; border-radius: 20px;"
            for btn in list(self.section_buttons.values()) + [self.help_btn]:
                btn.setStyleSheet(btn_style)
            self.logout_btn.setStyleSheet("padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #ef5350; border-radius: 20px;")
        self.refresh_dashboard()

    def logout(self):
        self.close()

    def show_profile_menu(self):
        menu = QMenu(self)
        if self.theme == 'dark':
            menu.setStyleSheet("""
            QMenu {
                background-color: #0a0f1c;
                color: #e6e6e6;
                border: 1px solid #2c3b55;
                border-radius: 8px;
            }
            QMenu::item:selected {
                background-color: #5a8dee;
            }
        """)
        else:
            menu.setStyleSheet("""
            QMenu {
                background-color: #f9f9f9;
                color: #021526;
                border: 1px solid #6eacda;
                border-radius: 8px;
            }
            QMenu::item:selected {
                background-color: #03346e;
                color: white;
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
        self.profile_btn.setText(f"{self.user['prenom']} {self.user['nom']} ▼")
        # Recreate avatar
        avatar_pixmap = QPixmap(36, 36)
        avatar_pixmap.fill(Qt.transparent)
        painter = QPainter(avatar_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor("#6eacda")))
        painter.setPen(QColor("#03346e"))
        painter.drawEllipse(1, 1, 34, 34)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
        initial = f"{self.user['prenom'][0]}{self.user['nom'][0]}"
        painter.drawText(avatar_pixmap.rect(), Qt.AlignCenter, initial)
        painter.end()
        self.profile_btn.setIcon(QIcon(avatar_pixmap))

    def switch_section(self, section):
        if self.theme == 'dark':
            inactive_style = "padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #e6e6e6; border-radius: 20px;"
            active_style = "padding: 12px; text-align: left; font-weight: bold; background-color: #5a8dee; color: white; border-radius: 20px;"
        else:
            inactive_style = "padding: 12px; text-align: left; font-weight: bold; background-color: transparent; color: #021526; border-radius: 20px;"
            active_style = "padding: 12px; text-align: left; font-weight: bold; background-color: #6eacda; color: white; border-radius: 20px;"
        for btn in self.section_buttons.values():
            btn.setStyleSheet(inactive_style)
        self.section_buttons[section].setStyleSheet(active_style)
        self.title_label.setText(section)
        if section == 'Dashboard':
            self.content.setCurrentWidget(self.dashboard_widget)
            #self.check_low_stock()
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
    def show_search(self):
        QMessageBox.information(self, "Recherche", "Fonction de recherche globale à implémenter.")

    def show_notifications(self):
        low_stocks = [p for p in get_all_products() if p['quantite_stock'] < 50]
        menu = QMenu(self)
        if self.theme == 'light':
            menu_style = """
QMenu {
    background-color: #f9f9f9;
    color: #021526;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
}
QMenu::item:selected {
    background-color: #03346e;
    color: white;
}
"""
            text_color = "#021526"
            sub_color = "#888888"
        else:
            menu_style = """
QMenu {
    background-color: #0a0f1c;
    color: #e6e6e6;
    border: 1px solid #2c3b55;
    border-radius: 8px;
}
QMenu::item:selected {
    background-color: #5a8dee;
    color: #e6e6e6;
}
"""
            text_color = "#e6e6e6"
            sub_color = "#2c3b55"
        menu.setStyleSheet(menu_style)

        # Header: Notifications
        header_action = QWidgetAction(menu)
        header_widget = QLabel("Notifications")
        header_widget.setStyleSheet(f"font-size: 16px; font-weight: bold; padding: 5px; color: {text_color};")
        header_action.setDefaultWidget(header_widget)
        menu.addAction(header_action)

        # Unread count
        unread_action = QWidgetAction(menu)
        unread_label = QLabel(f"You have {len(low_stocks)} low stock alerts")
        unread_label.setStyleSheet(f"color: {sub_color}; padding: 5px;")
        unread_action.setDefaultWidget(unread_label)
        menu.addAction(unread_action)

        # Separator
        menu.addSeparator()

        # NEW section
        new_label_action = QWidgetAction(menu)
        new_label = QLabel("NEW")
        new_label.setStyleSheet(f"color: {sub_color}; font-size: 12px; padding: 5px;")
        new_label_action.setDefaultWidget(new_label)
        menu.addAction(new_label_action)

        if low_stocks:
            for p in low_stocks:
                item_action = QWidgetAction(menu)
                item_widget = QWidget()
                item_layout = QHBoxLayout(item_widget)
                item_layout.setContentsMargins(5, 5, 5, 5)
                item_layout.setSpacing(10)

                # Icon (warning icon)
                icon_label = QLabel()
                icon_label.setPixmap(QIcon.fromTheme("dialog-warning").pixmap(24, 24))
                item_layout.addWidget(icon_label)

                # Text
                text_vbox = QVBoxLayout()
                title_label = QLabel(f"Stock bas pour {p['nom']}")
                title_label.setStyleSheet(f"font-weight: bold; color: {text_color};")
                text_vbox.addWidget(title_label)
                detail_label = QLabel(f"Quantité: {p['quantite_stock']}")
                detail_label.setStyleSheet(f"color: {sub_color}; font-size: 12px;")
                text_vbox.addWidget(detail_label)
                item_layout.addLayout(text_vbox)

                item_action.setDefaultWidget(item_widget)
                menu.addAction(item_action)
        else:
            no_notif_action = QWidgetAction(menu)
            no_notif_widget = QLabel("Aucune notification.")
            no_notif_widget.setStyleSheet(f"padding: 5px; color: {sub_color};")
            no_notif_action.setDefaultWidget(no_notif_widget)
            menu.addAction(no_notif_action)

        # BEFORE THAT (if needed, but omitted for simplicity)

        # View all at bottom
        menu.addSeparator()
        view_all = menu.addAction("View all")
        # Optionally connect view_all.triggered to a function

        # Show the menu below the button
        menu.exec_(self.notification_btn.mapToGlobal(QPoint(0, self.notification_btn.height())))

        self.update_notification_count()

    def update_notification_count(self):
        low_stocks = len([p for p in get_all_products() if p['quantite_stock'] < 50])
        if low_stocks > 0:
            self.notification_badge.setText(str(low_stocks))
            self.notification_badge.setVisible(True)
        else:
            self.notification_badge.setVisible(False)

    def show_help(self):
        QMessageBox.information(self, "Help", "Documentation et aide pour l'application.")