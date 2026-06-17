"""Tests for UI element safety checks"""
import pytest
from PySide6.QtWidgets import QApplication
from pos_app.views.safe_sales_wrapper import SafeSalesWrapper

# Shared QApplication fixture
@pytest.fixture(scope="module")
def qt_app():
    app = QApplication.instance() or QApplication([])
    yield app
    # Don't quit to avoid singleton issues

@pytest.fixture
def clean_widget(qt_app):
    """Fixture providing clean SafeSalesWidget instance"""
    widget = SafeSalesWrapper(None)
    yield widget
    widget.deleteLater()

def test_missing_amount_input(clean_widget):
    """Test handling of missing amount_paid_input"""
    clean_widget.amount_paid_input = None
    
    with pytest.raises(ValueError):
        clean_widget._update_totals()

def test_missing_change_label(clean_widget):
    """Test handling of missing change_label"""
    clean_widget.change_label = None
    
    # Should not crash, just skip update
    clean_widget._update_totals()
