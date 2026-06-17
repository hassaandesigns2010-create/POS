try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QTableWidget, QTableWidgetItem, QComboBox, QDoubleSpinBox,
        QFrame, QMessageBox, QDialog, QFormLayout, QLineEdit,
        QDateEdit, QTextEdit, QTabWidget, QCheckBox, QSpinBox,
        QHeaderView, QAbstractItemView
    )
    from PySide6.QtCore import Qt, QDate
except ImportError:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QTableWidget, QTableWidgetItem, QComboBox, QDoubleSpinBox,
        QFrame, QMessageBox, QDialog, QFormLayout, QLineEdit,
        QDateEdit, QTextEdit, QTabWidget, QCheckBox, QSpinBox,
        QHeaderView, QAbstractItemView
    )
    from PyQt6.QtCore import Qt, QDate
from datetime import datetime
import logging

class WarehouseRetailInventoryWidget(QWidget):
    """
    Refactored to support Unified Stock Model.
    Provides a global view of stock and movement history.
    """
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("📦 Global Inventory & Stock Movements")
        header.setProperty('role', 'heading')
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #f8fafc;")
        layout.addWidget(header)

        # Tabs
        self.tabs = QTabWidget()
        
        # Global Stock Tab
        stock_tab = self.create_stock_tab()
        self.tabs.addTab(stock_tab, "📦 Current Stock")
        
        # Stock Movements
        movements_tab = self.create_movements_tab()
        self.tabs.addTab(movements_tab, "📊 Stock Movements History")
        
        layout.addWidget(self.tabs)

    def create_stock_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Summary
        summary_frame = QFrame()
        summary_frame.setProperty('role', 'card')
        summary_layout = QHBoxLayout(summary_frame)
        
        # Total value
        value_frame = QFrame()
        value_frame.setProperty('role', 'card')
        value_layout = QVBoxLayout(value_frame)
        self.total_value_label = QLabel("Rs 0.00")
        self.total_value_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #3b82f6;")
        value_layout.addWidget(QLabel("💰 Total Inventory Value"))
        value_layout.addWidget(self.total_value_label)
        
        # Total items
        items_frame = QFrame()
        items_frame.setProperty('role', 'card')
        items_layout = QVBoxLayout(items_frame)
        self.total_items_label = QLabel("0")
        self.total_items_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #10b981;")
        items_layout.addWidget(QLabel("📦 Total Units in Stock"))
        items_layout.addWidget(self.total_items_label)
        
        # Low stock
        alerts_frame = QFrame()
        alerts_frame.setProperty('role', 'card')
        alerts_layout = QVBoxLayout(alerts_frame)
        self.low_stock_label = QLabel("0")
        self.low_stock_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #ef4444;")
        alerts_layout.addWidget(QLabel("⚠️ Low Stock Alerts"))
        alerts_layout.addWidget(self.low_stock_label)
        
        summary_layout.addWidget(value_frame)
        summary_layout.addWidget(items_frame)
        summary_layout.addWidget(alerts_frame)
        layout.addWidget(summary_frame)

        # Actions
        actions_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Refresh Data")
        refresh_btn.clicked.connect(self.load_inventory)
        actions_layout.addWidget(refresh_btn)
        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        # Table
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(7)
        self.stock_table.setHorizontalHeaderLabels([
            "Product Name", "SKU", "Total Stock", "Location", "Reorder Level", 
            "Total Value", "Status"
        ])
        self.stock_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.stock_table)
        self.load_inventory()
        return widget

    def create_movements_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Filters
        filter_frame = QFrame()
        filter_frame.setProperty('role', 'card')
        filter_layout = QHBoxLayout(filter_frame)
        
        filter_layout.addWidget(QLabel("Type:"))
        self.movement_type_filter = QComboBox()
        self.movement_type_filter.addItems(["All Types", "IN", "OUT", "ADJUSTMENT"])
        filter_layout.addWidget(self.movement_type_filter)
        
        filter_btn = QPushButton("🔍 Filter")
        filter_btn.clicked.connect(self.load_stock_movements)
        filter_layout.addWidget(filter_btn)
        filter_layout.addStretch()
        layout.addWidget(filter_frame)

        # Movements table
        self.movements_table = QTableWidget()
        self.movements_table.setColumnCount(6)
        self.movements_table.setHorizontalHeaderLabels([
            "Date", "Product", "Type", "Quantity", "Reference", "Notes"
        ])
        self.movements_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.movements_table)
        self.load_stock_movements()
        return widget

    def load_inventory(self):
        try:
            from pos_app.models.database import Product
            products = self.controller.session.query(Product).filter(Product.is_active == True).all()
            
            self.stock_table.setRowCount(len(products))
            total_val = 0
            total_qty = 0
            low_count = 0
            
            for i, p in enumerate(products):
                name_item = QTableWidgetItem(p.name)
                self.stock_table.setItem(i, 0, name_item)
                self.stock_table.setItem(i, 1, QTableWidgetItem(p.sku or ""))
                
                stock = p.stock_level or 0
                total_qty += stock
                reorder = p.reorder_level or 0
                
                stock_item = QTableWidgetItem(str(stock))
                if stock <= reorder:
                    stock_item.setForeground(Qt.red)
                    low_count += 1
                self.stock_table.setItem(i, 2, stock_item)
                
                loc = []
                if p.warehouse_location: loc.append(p.warehouse_location)
                if p.shelf_location: loc.append(p.shelf_location)
                self.stock_table.setItem(i, 3, QTableWidgetItem(", ".join(loc)))
                
                self.stock_table.setItem(i, 4, QTableWidgetItem(str(reorder)))
                
                val = stock * (p.purchase_price or 0)
                total_val += val
                self.stock_table.setItem(i, 5, QTableWidgetItem(f"Rs {val:,.2f}"))
                
                status = "Low Stock" if stock <= reorder else "Normal"
                status_item = QTableWidgetItem(status)
                if status == "Low Stock":
                    status_item.setForeground(Qt.red)
                self.stock_table.setItem(i, 6, status_item)
            
            self.total_value_label.setText(f"Rs {total_val:,.2f}")
            self.total_items_label.setText(f"{total_qty:,}")
            self.low_stock_label.setText(str(low_count))
            
        except Exception as e:
            print(f"Error loading global inventory: {e}")

    def load_stock_movements(self):
        try:
            from pos_app.models.database import StockMovement, Product
            query = self.controller.session.query(StockMovement).join(Product)
            
            m_type = self.movement_type_filter.currentText()
            if m_type != "All Types":
                query = query.filter(StockMovement.movement_type == m_type)
                
            movements = query.order_by(StockMovement.date.desc()).limit(100).all()
            self.movements_table.setRowCount(len(movements))
            
            for i, m in enumerate(movements):
                self.movements_table.setItem(i, 0, QTableWidgetItem(m.date.strftime('%Y-%m-%d %H:%M') if m.date else ""))
                self.movements_table.setItem(i, 1, QTableWidgetItem(m.product.name if m.product else "Unknown"))
                self.movements_table.setItem(i, 2, QTableWidgetItem(m.movement_type))
                
                qty_item = QTableWidgetItem(str(abs(m.quantity)))
                if m.movement_type == "OUT":
                    qty_item.setForeground(Qt.red)
                elif m.movement_type == "IN":
                    qty_item.setForeground(Qt.green)
                self.movements_table.setItem(i, 3, qty_item)
                
                self.movements_table.setItem(i, 4, QTableWidgetItem(m.reference or ""))
                self.movements_table.setItem(i, 5, QTableWidgetItem(m.notes or ""))
        except Exception as e:
            print(f"Error loading movements: {e}")
