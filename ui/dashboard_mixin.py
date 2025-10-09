# dashboard_mixin.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGraphicsOpacityEffect, QGraphicsDropShadowEffect, QScrollArea
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from bson import ObjectId
from database import get_kpi, get_stock_by_category, get_all_entries, get_all_exits, get_all_products, DB
import matplotlib.pyplot as plt  # nécessaire pour les couleurs du pie chart

class DashboardMixin:
    def create_dashboard(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        widget = QWidget()
        scroll.setWidget(widget)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)

        # --- Greeting ---
        greeting = QLabel(f"Bonjour, {self.user['prenom']} bienvenue!")
        text_color = "#e6e6e6" if self.theme == 'dark' else "#021526"
        greeting.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {text_color};")
        layout.addWidget(greeting)

        # --- KPI ---
        kpi = get_kpi()
        kpi_layout = QGridLayout()
        kpi_layout.setSpacing(25)
        cards = [
            (f"Total Produits\n{kpi['total_prods']}", "#ba68c8"),
            (f"Ruptures Stock\n{kpi['rupture']}", "#ef5350"),
            (f"Entrées Récentes\n{kpi['recent_entries']}", "#66bb6a"),
            (f"Sorties Récentes\n{kpi['recent_exits']}", "#ffa726")
        ]
        for i, (text, color) in enumerate(cards):
            card = QFrame()
            bg_color = "rgba(255,255,255,0.05)" if self.theme == 'dark' else "rgba(0,0,0,0.05)"
            hover_color = "rgba(100, 100, 255, 0.1)"
            card.setStyleSheet(f'''
                QFrame {{
                    background-color: {bg_color};
                    border-radius: 12px;
                    padding: 25px;
                }}
                QFrame:hover {{
                    background-color: {hover_color};
                }}
            ''')
            card.setGraphicsEffect(self.create_shadow_effect())

            card_layout = QVBoxLayout(card)
            label = QLabel(text, alignment=Qt.AlignCenter)
            label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
            card_layout.addWidget(label)
            kpi_layout.addWidget(card, i // 2, i % 2)
        layout.addLayout(kpi_layout)

        # --- Graphiques : pie + bar ---
        chart_layout = QHBoxLayout()
        chart_layout.addWidget(self.create_pie_chart_view(), stretch=1)
        chart_layout.addWidget(self.create_bar_chart_view(), stretch=2)
        layout.addLayout(chart_layout)

        # --- Derniers mouvements ---
        recent_label = QLabel("Derniers mouvements")
        recent_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {text_color}; margin-top: 20px;")
        layout.addWidget(recent_label)

        recent_table = QTableWidget()
        recent_table.setColumnCount(4)
        recent_table.setHorizontalHeaderLabels(['Type', 'Produit', 'Quantité', 'Date'])
        recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        recent_table.setAlternatingRowColors(True)
        recent_table.setStyleSheet(f"alternate-background-color: rgba(255,255,255,0.05);" if self.theme == 'dark' else "alternate-background-color: rgba(0,0,0,0.05);")

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
        movements = movements[:10]  # Increased to 10 for more data

        recent_table.setRowCount(len(movements))
        for i, m in enumerate(movements):
            product = DB['produits'].find_one({'_id': ObjectId(m['produit_id'])}) or {}
            nom = product.get('nom', 'Inconnu')
            recent_table.setItem(i, 0, QTableWidgetItem(m['type']))
            recent_table.setItem(i, 1, QTableWidgetItem(nom))
            recent_table.setItem(i, 2, QTableWidgetItem(str(m['quantite'])))
            recent_table.setItem(i, 3, QTableWidgetItem(m['date'].strftime('%Y-%m-%d')))
        recent_table.setMaximumHeight(200)  # Limit height to encourage scrolling
        layout.addWidget(recent_table)

        # --- Alertes stock faible ---
        low_stocks = [p for p in get_all_products() if p['quantite_stock'] < 50]
        if low_stocks:
            alert_label = QLabel("⚠️ Produits à stock faible : " + ", ".join(p['nom'] for p in low_stocks[:5]))
            alert_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px; padding: 10px; background-color: rgba(255,0,0,0.1); border-radius: 8px; margin-top: 10px;")
            layout.addWidget(alert_label)

        # --- Animation fade-in ---
        self.animate_widget(widget)
        return scroll

    # --- Refresh dashboard ---
    def refresh_dashboard(self):
        self.content.removeWidget(self.dashboard_widget)
        self.dashboard_widget.deleteLater()
        self.dashboard_widget = self.create_dashboard()
        self.content.insertWidget(0, self.dashboard_widget)
        if self.content.currentWidget() == self.dashboard_widget or self.section_buttons['Dashboard'].styleSheet().find('#3498db') != -1:
            self.content.setCurrentWidget(self.dashboard_widget)

    # --- Shadow effect ---
    def create_shadow_effect(self):
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(20)
        effect.setColor(QColor(0, 0, 0, 100))
        effect.setOffset(0, 3)
        return effect

    # --- Fade-in animation ---
    def animate_widget(self, widget):
        opacity_effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(opacity_effect)
        animation = QPropertyAnimation(opacity_effect, b"opacity")
        animation.setDuration(800)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()

    # --- Graphiques ---
    def create_pie_chart_view(self):
        fig = Figure(figsize=(6,6), dpi=100)
        ax = fig.add_subplot(111)
        stock_data = get_stock_by_category()
        categories = list(stock_data.keys())
        values = list(stock_data.values())
        
        # Modern pie chart with explode, shadow, and theme-aware colors
        colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))  # Modern color map
        wedges, texts, autotexts = ax.pie(values, labels=categories, autopct='%1.1f%%', 
                                          startangle=90, explode=[0.05]*len(categories), 
                                          colors=colors, shadow=True, textprops={'fontsize': 10})
        
        # Improve label readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title("Répartition du stock par catégorie", fontsize=10, fontweight='bold', pad=20)
        ax.axis('equal')
        
        # Transparent background for theme integration
        fig.patch.set_alpha(0)
        ax.set_facecolor('none')
        
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(400)
        return canvas

    def create_bar_chart_view(self):
        fig = Figure(figsize=(8,5), dpi=100)
        ax = fig.add_subplot(111)
        stock_data = get_stock_by_category()
        categories = list(stock_data.keys())
        values = list(stock_data.values())
        x = np.arange(len(categories))
        
        # Modern bar with gradient-like alpha and theme color
        color = "#8e24aa" if self.theme == 'dark' else "#7b1fa2"
        bars = ax.bar(x, values, color=color, alpha=0.7, edgecolor='white', linewidth=1.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=10)
        ax.set_title("Stock global par catégorie", fontsize=10, fontweight='bold', pad=20)
        
        # Clean spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#aaa')
        ax.tick_params(axis='y', colors='#777')
        
        # Transparent background
        fig.patch.set_alpha(0)
        ax.set_facecolor('none')
        
        fig.tight_layout()
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(400)
        return canvas

    # --- Vérification stock faible ---
    def check_low_stock(self):
        low = [p for p in get_all_products() if p['quantite_stock'] < 50]
        if low:
            names = ", ".join(p['nom'] for p in low)
            QMessageBox.warning(self, "Alerte Stock Bas", f"Les produits suivants ont un stock bas (<50): {names}")