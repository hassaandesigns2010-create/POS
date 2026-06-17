#!/usr/bin/env python3
"""
Comprehensive test suite for POS navigation and keyboard shortcuts.
Tests all the fixes implemented for:
1. Search suggestions arrow key navigation
2. Up arrow navigation from cart to search bar
3. Keyboard shortcuts when editing cart cells
"""

import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock

# Try to import Qt frameworks with the same fallback pattern as the main code
try:
    from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QListWidget, QTableWidget, QComboBox
    from PySide6.QtCore import Qt, QTimer, QEvent
    from PySide6.QtTest import QTest
    from PySide6.QtGui import QKeyEvent
    QT_FRAMEWORK = "PySide6"
except ImportError:
    from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QListWidget, QTableWidget, QComboBox
    from PyQt6.QtCore import Qt, QTimer, QEvent
    from PyQt6.QtTest import QTest
    from PyQt6.QtGui import QKeyEvent
    QT_FRAMEWORK = "PyQt6"

# Add the parent directory to the path to import pos_app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class NavigationTestSuite:
    """Test suite for POS navigation and shortcuts"""
    
    def __init__(self):
        self.app = None
        self.sales_widget = None
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        status = "PASS" if passed else "FAIL"
        self.test_results.append(f"{status}: {test_name} - {details}")
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        print(f"{status}: {test_name} - {details}")
    
    def setup_test_environment(self):
        """Setup test environment with mocked dependencies"""
        try:
            # Create QApplication if it doesn't exist
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            
            # Create a mock controller
            mock_controller = Mock()
            mock_session = Mock()
            mock_controller.session = mock_session
            
            # Mock database queries for products
            mock_product = Mock()
            mock_product.id = 1
            mock_product.name = "Test Product"
            mock_product.sku = "TEST001"
            mock_product.barcode = "123456789"
            mock_product.price = 10.0
            
            # Create a proper mock for the filter chain
            mock_filter = Mock()
            
            def mock_ilike(pattern):
                # Just return the mock filter for any pattern
                return mock_filter
            
            mock_filter.ilike = mock_ilike
            mock_filter.__or__ = lambda self, other: mock_filter
            mock_filter.__and__ = lambda self, other: mock_filter
            mock_filter.limit.return_value = mock_filter
            mock_filter.all.return_value = [mock_product]
            
            mock_query = Mock()
            mock_query.filter.return_value = mock_filter
            mock_session.query.return_value = mock_query
            
            # Import and create SalesWidget
            from pos_app.views.sales import SalesWidget
            self.sales_widget = SalesWidget(mock_controller)
                
            return True
        except Exception as e:
            print(f"Failed to setup test environment: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_search_suggestions_arrow_navigation(self):
        """Test 1: Search suggestions arrow key navigation and highlighting"""
        print("\n=== Test 1: Search Suggestions Arrow Navigation ===")
        
        try:
            # Get the search input and suggestions list
            search_input = self.sales_widget.product_search
            suggestions_list = self.sales_widget.search_suggestions_list
            
            # Simulate typing in search to trigger suggestions
            search_input.setText("Test")
            self.sales_widget.search_products()
            
            # Wait for suggestions to populate
            QApplication.processEvents()
            time.sleep(0.1)
            
            # Test down arrow from search input to suggestions
            suggestions_count = suggestions_list.count()
            if suggestions_count > 0:
                # Focus search input
                search_input.setFocus()
                search_input.selectAll()
                
                # Send down arrow key
                key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Down, Qt.KeyboardModifier.NoModifier)
                QApplication.sendEvent(search_input, key_event)
                QApplication.processEvents()
                
                # Check if suggestions list has focus and first item is selected
                has_focus = suggestions_list.hasFocus()
                current_row = suggestions_list.currentRow()
                first_item_selected = suggestions_list.item(0).isSelected() if suggestions_list.item(0) else False
                
                self.log_test("Down arrow from search to suggestions", 
                            has_focus and current_row == 0 and first_item_selected,
                            f"Focus: {has_focus}, Row: {current_row}, Selected: {first_item_selected}")
                
                # Test down arrow within suggestions
                if suggestions_count > 1:
                    key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Down, Qt.KeyboardModifier.NoModifier)
                    QApplication.sendEvent(suggestions_list, key_event)
                    QApplication.processEvents()
                    
                    new_row = suggestions_list.currentRow()
                    second_item_selected = suggestions_list.item(1).isSelected() if suggestions_list.item(1) else False
                    
                    self.log_test("Down arrow within suggestions", 
                                new_row == 1 and second_item_selected,
                                f"Row: {new_row}, Selected: {second_item_selected}")
                
                # Test up arrow within suggestions
                key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Up, Qt.KeyboardModifier.NoModifier)
                QApplication.sendEvent(suggestions_list, key_event)
                QApplication.processEvents()
                
                back_row = suggestions_list.currentRow()
                first_item_selected_again = suggestions_list.item(0).isSelected() if suggestions_list.item(0) else False
                
                self.log_test("Up arrow within suggestions", 
                            back_row == 0 and first_item_selected_again,
                            f"Row: {back_row}, Selected: {first_item_selected_again}")
                
                # Test up arrow from first suggestion back to search
                key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Up, Qt.KeyboardModifier.NoModifier)
                QApplication.sendEvent(suggestions_list, key_event)
                QApplication.processEvents()
                
                search_has_focus = search_input.hasFocus()
                
                self.log_test("Up arrow from suggestions to search", 
                            search_has_focus,
                            f"Search focus: {search_has_focus}")
            else:
                self.log_test("Search suggestions population", False, "No suggestions found")
                
        except Exception as e:
            self.log_test("Search suggestions navigation", False, f"Exception: {e}")
    
    def test_cart_to_search_navigation(self):
        """Test 2: Up arrow navigation from cart products back to search bar"""
        print("\n=== Test 2: Cart to Search Navigation ===")
        
        try:
            # Add a test product to cart
            test_product = {
                'id': 1,
                'name': 'Test Product',
                'quantity': 2,
                'price': 10.0,
                'total': 20.0
            }
            self.sales_widget.current_cart = [test_product]
            self.sales_widget.update_cart_table()
            QApplication.processEvents()
            
            cart_table = self.sales_widget.cart_table
            search_input = self.sales_widget.product_search
            
            # Focus cart table and select first row
            cart_table.setFocus()
            cart_table.selectRow(0)
            QApplication.processEvents()
            
            # Test up arrow from cart first row to search
            key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Up, Qt.KeyboardModifier.NoModifier)
            QApplication.sendEvent(cart_table, key_event)
            QApplication.processEvents()
            
            search_has_focus = search_input.hasFocus()
            search_selected = search_input.selectedText() != ""
            
            self.log_test("Up arrow from cart to search", 
                        search_has_focus and search_selected,
                        f"Search focus: {search_has_focus}, Text selected: {search_selected}")
            
            # Test normal up arrow within cart (from second row to first)
            if cart_table.rowCount() > 1:
                cart_table.setFocus()
                cart_table.selectRow(1)
                QApplication.processEvents()
                
                key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Up, Qt.KeyboardModifier.NoModifier)
                QApplication.sendEvent(cart_table, key_event)
                QApplication.processEvents()
                
                current_row = cart_table.currentRow()
                
                self.log_test("Up arrow within cart", 
                            current_row == 0,
                            f"Current row: {current_row}")
            
        except Exception as e:
            self.log_test("Cart to search navigation", False, f"Exception: {e}")
    
    def test_cart_editing_shortcuts(self):
        """Test 3: Keyboard shortcuts when editing cart cells"""
        print("\n=== Test 3: Cart Editing Shortcuts ===")
        
        try:
            # Setup cart with test product
            test_product = {
                'id': 1,
                'name': 'Test Product',
                'quantity': 2,
                'price': 10.0,
                'total': 20.0
            }
            self.sales_widget.current_cart = [test_product]
            self.sales_widget.update_cart_table()
            QApplication.processEvents()
            
            cart_table = self.sales_widget.cart_table
            pay_method_combo = self.sales_widget.pay_method_combo
            
            # Get initial payment method
            initial_payment_method = pay_method_combo.currentText()
            
            # Simulate editing a cell (QTY column)
            cart_table.setFocus()
            cart_table.selectRow(0)
            cart_table.setCurrentCell(0, 1)  # QTY column
            # Use editItem instead of editCell
            item = cart_table.item(0, 1)
            if item:
                cart_table.editItem(item)
            QApplication.processEvents()
            
            # Check if table is in editing state
            is_editing = cart_table.state() == QTableWidget.EditingState
            self.log_test("Cart table enters editing state", is_editing, f"Editing state: {is_editing}")
            
            if is_editing:
                # Try Ctrl+C while editing - should NOT change payment method
                key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier)
                QApplication.sendEvent(cart_table, key_event)
                QApplication.processEvents()
                
                # Payment method should remain unchanged
                current_payment_method = pay_method_combo.currentText()
                payment_unchanged = current_payment_method == initial_payment_method
                
                self.log_test("Ctrl+C during editing doesn't change payment", 
                            payment_unchanged,
                            f"Initial: {initial_payment_method}, Current: {current_payment_method}")
                
                # Stop editing
                cart_table.closePersistentEditor(cart_table.currentItem())
                QApplication.processEvents()
                
                # Now try Ctrl+C when NOT editing - should change payment method
                key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier)
                QApplication.sendEvent(cart_table, key_event)
                QApplication.processEvents()
                
                new_payment_method = pay_method_combo.currentText()
                payment_changed = new_payment_method != initial_payment_method
                
                self.log_test("Ctrl+C when not editing changes payment", 
                            payment_changed,
                            f"Initial: {initial_payment_method}, New: {new_payment_method}")
            else:
                self.log_test("Cell editing simulation", False, "Could not enter editing state")
            
        except Exception as e:
            self.log_test("Cart editing shortcuts", False, f"Exception: {e}")
    
    def test_complete_workflow(self):
        """Test 4: Complete workflow with all navigation features"""
        print("\n=== Test 4: Complete Navigation Workflow ===")
        
        try:
            search_input = self.sales_widget.product_search
            suggestions_list = self.sales_widget.search_suggestions_list
            cart_table = self.sales_widget.cart_table
            
            # Step 1: Search for product
            search_input.setText("Test")
            search_input.setFocus()
            self.sales_widget.search_products()
            QApplication.processEvents()
            time.sleep(0.1)
            
            # Step 2: Navigate to suggestions with down arrow
            key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Down, Qt.KeyboardModifier.NoModifier)
            QApplication.sendEvent(search_input, key_event)
            QApplication.processEvents()
            
            suggestions_focused = suggestions_list.hasFocus()
            self.log_test("Workflow: Search to suggestions", suggestions_focused)
            
            # Step 3: Select suggestion with Enter
            if suggestions_list.count() > 0:
                suggestions_list.setCurrentRow(0)
                key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Enter, Qt.KeyboardModifier.NoModifier)
                QApplication.sendEvent(suggestions_list, key_event)
                QApplication.processEvents()
                
                # Check if product was added to cart
                cart_has_items = len(self.sales_widget.current_cart) > 0
                self.log_test("Workflow: Add product via Enter", cart_has_items)
                
                if cart_has_items:
                    # Step 4: Navigate to cart with right arrow
                    key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Right, Qt.KeyboardModifier.NoModifier)
                    QApplication.sendEvent(suggestions_list, key_event)
                    QApplication.processEvents()
                    
                    cart_focused = cart_table.hasFocus()
                    self.log_test("Workflow: Suggestions to cart", cart_focused)
                    
                    # Step 5: Navigate back to search with up arrow
                    if cart_focused:
                        cart_table.selectRow(0)
                        key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Up, Qt.KeyboardModifier.NoModifier)
                        QApplication.sendEvent(cart_table, key_event)
                        QApplication.processEvents()
                        
                        search_focused_again = search_input.hasFocus()
                        self.log_test("Workflow: Cart to search", search_focused_again)
            
        except Exception as e:
            self.log_test("Complete workflow", False, f"Exception: {e}")
    
    def test_payment_shortcut_context(self):
        """Test 5: Payment shortcut context awareness"""
        print("\n=== Test 5: Payment Shortcut Context Awareness ===")
        
        try:
            cart_table = self.sales_widget.cart_table
            pay_method_combo = self.sales_widget.pay_method_combo
            
            # Setup cart with items
            test_product = {
                'id': 1,
                'name': 'Test Product',
                'quantity': 2,
                'price': 10.0,
                'total': 20.0
            }
            self.sales_widget.current_cart = [test_product]
            self.sales_widget.update_cart_table()
            QApplication.processEvents()
            
            initial_method = pay_method_combo.currentText()
            
            # Test 1: Ctrl+C when not editing should change payment
            cart_table.setFocus()
            key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier)
            QApplication.sendEvent(cart_table, key_event)
            QApplication.processEvents()
            
            method_changed_1 = pay_method_combo.currentText() != initial_method
            self.log_test("Payment shortcut when not editing", method_changed_1)
            
            # Reset for next test
            pay_method_combo.setCurrentIndex(0)
            initial_method = pay_method_combo.currentText()
            
            # Test 2: Ctrl+C when editing should NOT change payment
            cart_table.setFocus()
            cart_table.selectRow(0)
            cart_table.setCurrentCell(0, 1)  # QTY column
            # Use editItem instead of editCell
            item = cart_table.item(0, 1)
            if item:
                cart_table.editItem(item)
            QApplication.processEvents()
            
            # Send Ctrl+C while editing
            key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier)
            QApplication.sendEvent(cart_table.viewport(), key_event)  # Send to viewport
            QApplication.processEvents()
            
            method_unchanged = pay_method_combo.currentText() == initial_method
            self.log_test("Payment shortcut when editing", method_unchanged)
            
        except Exception as e:
            self.log_test("Payment shortcut context", False, f"Exception: {e}")
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("=" * 60)
        print("POS NAVIGATION AND SHORTCUTS TEST SUITE")
        print("=" * 60)
        
        # Setup test environment
        if not self.setup_test_environment():
            print("FAILED: Could not setup test environment")
            return False
        
        # Run all tests
        self.test_search_suggestions_arrow_navigation()
        self.test_cart_to_search_navigation()
        self.test_cart_editing_shortcuts()
        self.test_complete_workflow()
        self.test_payment_shortcut_context()
        
        # Generate final report
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            print(f"  {result}")
        
        if self.failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! Navigation and shortcuts are working correctly.")
        else:
            print(f"\n⚠️  {self.failed_tests} test(s) failed. Please review the implementation.")
        
        return self.failed_tests == 0

def main():
    """Main function to run the test suite"""
    test_suite = NavigationTestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n✅ All navigation and shortcut fixes verified successfully!")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
