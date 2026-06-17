"""Table styling utilities for POS application"""
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

class TableStyler:
    """Utility class for styling table items"""
    
    @staticmethod
    def create_item(text, is_currency=False, is_numeric=False):
        """Create a styled table item"""
        item = QTableWidgetItem(str(text))
        
        if is_currency:
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            # Add currency formatting
            try:
                value = float(text) if text else 0.0
                item.setText(f"Rs {value:,.2f}")
            except (ValueError, TypeError):
                pass
        elif is_numeric:
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        return item
    
    @staticmethod
    def setup_product_table(table):
        """Setup professional styling for product table"""
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(True)
        table.setSelectionBehavior(table.SelectRows)
        table.setSelectionMode(table.SingleSelection)
        
        # Set column widths
        header = table.horizontalHeader()
        try:
            # PySide6
            header.setSectionResizeMode(0, header.ResizeMode.Fixed)  # SKU
            header.setSectionResizeMode(1, header.ResizeMode.Stretch)  # Name
            header.setSectionResizeMode(2, header.ResizeMode.Stretch)  # Description
            header.setSectionResizeMode(3, header.ResizeMode.Fixed)  # Retail Price
            header.setSectionResizeMode(4, header.ResizeMode.Fixed)  # Wholesale Price
            header.setSectionResizeMode(5, header.ResizeMode.Fixed)  # Stock
        except AttributeError:
            # PyQt6
            header.setSectionResizeMode(0, header.Fixed)
            header.setSectionResizeMode(1, header.Stretch)
            header.setSectionResizeMode(2, header.Stretch)
            header.setSectionResizeMode(3, header.Fixed)
            header.setSectionResizeMode(4, header.Fixed)
            header.setSectionResizeMode(5, header.Fixed)
        
        header.resizeSection(0, 80)   # SKU
        header.resizeSection(3, 100)  # Retail Price
        header.resizeSection(4, 100)  # Wholesale Price
        header.resizeSection(5, 80)   # Stock
