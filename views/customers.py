try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
        QLineEdit, QMessageBox, QComboBox, QDoubleSpinBox, QAbstractItemView
    )
    from PySide6.QtCore import Signal, Qt
except ImportError:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
        QLineEdit, QMessageBox, QComboBox, QDoubleSpinBox, QAbstractItemView
    )
    from PyQt6.QtCore import pyqtSignal as Signal, Qt
from pos_app.models.database import Customer, CustomerType


class CustomersWidget(QWidget):
    # quick actions
    action_receive_payment = Signal(int)  # customer_id
    action_export_statement = Signal(int)  # customer_id
    customer_added = Signal()  # Signal when new customer is added
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        # Ensure clean transaction state
        try:
            self.controller.session.rollback()
        except Exception as e:
            pass
        self.page_size = 12
        self.current_page = 0
        self._customers_cache = []
        self._filtered_customers = None
        self._last_sync_ts = None
        self.setup_ui()
        self.load_customers()
        self._init_sync_timer()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        header = QLabel("👥 Customer Management")
        header.setProperty('role', 'heading')
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        add_btn = QPushButton("✨ Add New Customer")
        add_btn.setProperty('accent', 'Qt.green')
        add_btn.setMinimumHeight(44)
        add_btn.clicked.connect(self.show_add_customer_dialog)
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)
        
        # Action buttons (initially disabled)
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 10, 0, 10)
        
        self.edit_customer_btn = QPushButton("✏️ Edit Customer")
        self.edit_customer_btn.setProperty('accent', 'Qt.blue')
        self.edit_customer_btn.setMinimumHeight(36)
        self.edit_customer_btn.setEnabled(False)
        self.edit_customer_btn.clicked.connect(self.edit_selected_customer)
        
        self.delete_customer_btn = QPushButton("🗑️ Delete Customer")
        self.delete_customer_btn.setProperty('accent', 'Qt.red')
        self.delete_customer_btn.setMinimumHeight(36)
        self.delete_customer_btn.setEnabled(False)
        self.delete_customer_btn.clicked.connect(self.delete_selected_customer)
        
        self.receive_payment_btn = QPushButton("💰 Receive Payment")
        self.receive_payment_btn.setProperty('accent', 'Qt.green')
        self.receive_payment_btn.setMinimumHeight(36)
        self.receive_payment_btn.setEnabled(False)
        self.receive_payment_btn.clicked.connect(self.receive_payment_selected)
        
        self.statement_btn = QPushButton("📄 Statement")
        self.statement_btn.setProperty('accent', 'orange')
        self.statement_btn.setMinimumHeight(36)
        self.statement_btn.setEnabled(False)
        self.statement_btn.clicked.connect(self.statement_selected)
        
        self.print_btn = QPushButton("🖨️ Print")
        self.print_btn.setProperty('accent', 'Qt.blue')
        self.print_btn.setMinimumHeight(36)
        self.print_btn.setEnabled(True)
        self.print_btn.clicked.connect(self.print_selected_customer)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setProperty('accent', 'Qt.gray')
        self.refresh_btn.setMinimumHeight(36)
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.clicked.connect(self.refresh_customers)
        
        actions_layout.addWidget(self.edit_customer_btn)
        actions_layout.addWidget(self.delete_customer_btn)
        actions_layout.addWidget(self.receive_payment_btn)
        actions_layout.addWidget(self.statement_btn)
        actions_layout.addWidget(self.print_btn)
        actions_layout.addWidget(self.refresh_btn)
        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        # Search + pagination
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Search customers... (type to search)')
        # Use debounced search instead of immediate filter to prevent UI freeze
        self._search_timer = None
        self.search_input.textChanged.connect(self._on_search_text_changed)
        search_layout.addWidget(self.search_input)

        self.prev_btn = QPushButton("Prev")
        self.next_btn = QPushButton("Next")
        self.page_label = QLabel("Page 1")
        self.prev_btn.clicked.connect(self._prev_page)
        self.next_btn.clicked.connect(self._next_page)
        search_layout.addStretch()
        search_layout.addWidget(self.prev_btn)
        search_layout.addWidget(self.page_label)
        search_layout.addWidget(self.next_btn)
        layout.addLayout(search_layout)

        # Customer Table (removed Actions column)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Name", "Type", "Contact", "Email",
            "Credit Limit", "Balance"
        ])
        
        # Table selection
        try:
            self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        except Exception:
            pass
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.selected_customer_id = None
        try:
            from PySide6.QtWidgets import QHeaderView
        except ImportError:
            from PyQt6.QtWidgets import QHeaderView
        
        try:
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table.horizontalHeader().setStretchLastSection(True)
            # Remove Actions column sizing
            self.table.verticalHeader().setVisible(False)
            self.table.setWordWrap(True)
        except Exception:
            pass
        try:
            from PySide6.QtCore import Qt
            self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        except Exception:
            pass
        layout.addWidget(self.table)

    def show_add_customer_dialog(self):
        dialog = CustomerDialog(self)
        if dialog.exec() == QDialog.Accepted:
            if not dialog.name_input.text().strip():
                QMessageBox.warning(self, "Validation", "Customer name is required.")
                return
            try:
                self.controller.add_customer(
                    name=dialog.name_input.text().strip(),
                    type=dialog.type_input.currentText().upper(),  # Use string directly
                    contact=dialog.contact_input.text().strip(),
                    email=dialog.email_input.text().strip(),
                    address=dialog.address_input.text().strip(),
                    credit_limit=dialog.credit_limit_input.value()
                )
                QMessageBox.information(self, "Success", "Customer added successfully!")
                # Commit so other sessions can see new customer
                try:
                    self.controller.session.commit()
                except Exception:
                    pass
                self.load_customers()
                # Emit signal to notify other widgets (like sales page) to refresh
                print("[DEBUG] Emitting customer_added signal...")
                self.customer_added.emit()
                print("[DEBUG] customer_added signal emitted")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def showEvent(self, event):
        try:
            self.load_customers()
        except Exception:
            pass
        super().showEvent(event)

    def load_customers(self):
        try:
            # Prefer controller method; fallback to direct session query for robustness
            if hasattr(self.controller, 'list_customers'):
                customers = self.controller.list_customers()
            else:
                try:
                    from pos_app.models.database import Customer
                    customers = self.controller.session.query(Customer).all()
                except Exception as qe:
                    print(f"Error querying customers: {qe}")
                    try:
                        self.controller.session.rollback()
                    except Exception as e:
                        pass
                    customers = []
            # cache and show first page
            self._customers_cache = customers
            self.current_page = 0
            self._filtered_customers = None
            self._update_page()
            # Rollback transaction to prevent leaks
            try:
                self.controller.session.rollback()
            except Exception:
                pass
        except Exception as e:
            print(f"Error loading customers: {e}")
            try:
                self.controller.session.rollback()
            except Exception as e:
                pass
            QMessageBox.critical(self, "Error", str(e))
        finally:
            try:
                self.controller.session.rollback()
            except Exception:
                pass

    def _on_search_text_changed(self, text):
        """Handle search text change with debouncing to prevent UI freeze"""
        try:
            from PySide6.QtCore import QTimer
        except ImportError:
            from PyQt6.QtCore import QTimer

        # Initialize timer if it doesn't exist
        if not hasattr(self, '_search_timer') or self._search_timer is None:
            self._search_timer = QTimer(self)
            self._search_timer.setSingleShot(True)
            self._search_timer.timeout.connect(self._perform_search)
        
        # Store the search text for the timer to use
        self._pending_search_text = text
        
        # Restart the timer with debounce delay
        self._search_timer.stop()
        self._search_timer.start(450)  # 450ms debounce
        
    def _perform_search(self):
        """Execute the actual filtering after the debounce delay"""
        try:
            self.apply_filter(self._pending_search_text)
        except Exception:
            pass

    def apply_filter(self, text):
        try:
            text = (text or "").strip().lower()
            if not hasattr(self, '_customers_cache') or self._customers_cache is None:
                return
            filtered = [c for c in self._customers_cache if text in (c.name or '').lower() or text in (c.contact or '').lower()]
            self._filtered_customers = filtered
            self.current_page = 0
            self._update_page()
        except Exception as e:
            print(f"Error in customer filter: {e}")
            return

    def _update_page(self):
        """Update table with current page of customers"""
        try:
            from PySide6.QtCore import Qt
        except ImportError:
            from PyQt6.QtCore import Qt
        
        items = self._filtered_customers if self._filtered_customers is not None else self._customers_cache
        start = self.current_page * self.page_size
        end = start + self.page_size
        page_items = items[start:end]
        
        self.table.setRowCount(len(page_items))
        for i, c in enumerate(page_items):
            # Create items with centered alignment
            # Column 0: Name
            name_item = QTableWidgetItem(c.name or "")
            name_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, name_item)
            
            # Column 1: Type (customer type - retail/wholesale)
            customer_type = getattr(c, 'type', 'RETAIL') or 'RETAIL'
            # Display in title case for better readability
            display_type = customer_type.title() if customer_type else 'Retail'
            type_item = QTableWidgetItem(display_type)
            type_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 1, type_item)
            
            # Column 2: Contact (phone)
            contact_item = QTableWidgetItem(c.contact or "")
            contact_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 2, contact_item)
            
            # Column 3: Email
            email_item = QTableWidgetItem(getattr(c, 'email', '') or "")
            email_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, email_item)
            
            # Column 4: Credit Limit
            credit_limit = getattr(c, 'credit_limit', 0.0) or 0.0
            credit_limit_item = QTableWidgetItem(f"{credit_limit:.2f}")
            credit_limit_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 4, credit_limit_item)
            
            # Column 5: Balance (current outstanding balance from database)
            # current_credit already represents the actual outstanding balance
            balance = getattr(c, 'current_credit', 0.0) or 0.0
            balance_item = QTableWidgetItem(f"{balance:.2f}")
            balance_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 5, balance_item)
            
            # Store customer ID for selection handling
            item = self.table.item(i, 0)
            if item:
                item.setData(Qt.UserRole, c.id)
            try:
                self.table.setRowHeight(i, 36)
            except Exception:
                pass
        total_pages = max(1, (len(items) + self.page_size - 1) // self.page_size)
        self.page_label.setText(f"Page {self.current_page+1} / {total_pages}")
        
        # Auto-select first row if there's only one item and ensure correct ID is set
        if len(page_items) == 1:
            self.table.selectRow(0)
            # Always ensure selected_customer_id is set correctly for single result
            self.selected_customer_id = page_items[0].id
            self.edit_customer_btn.setEnabled(True)
            self.delete_customer_btn.setEnabled(True)
            self.receive_payment_btn.setEnabled(True)
            self.statement_btn.setEnabled(True)
            self.print_btn.setEnabled(True)
            print(f"[DEBUG] Auto-selected single customer: ID={self.selected_customer_id}")
    
    def _init_sync_timer(self):
        """Poll sync_state and refresh customers when data changes on other machines."""
        try:
            from PySide6.QtCore import QTimer
        except ImportError:
            from PyQt6.QtCore import QTimer
        
        try:
            self._sync_timer = QTimer(self)
            self._sync_timer.setInterval(5000)  # 5 seconds
            self._sync_timer.timeout.connect(self._check_for_remote_changes)
            self._sync_timer.start()
        except Exception:
            self._sync_timer = None

    def _check_for_remote_changes(self):
        try:
            from pos_app.models.database import get_sync_timestamp
            ts = get_sync_timestamp(self.controller.session, 'customers')
            
            # Rollback immediately to prevent keeping transaction open
            try:
                self.controller.session.rollback()
            except Exception:
                pass

            if ts is None:
                return
            if self._last_sync_ts is None or ts > self._last_sync_ts:
                self._last_sync_ts = ts
                self.load_customers()
        except Exception:
            try:
                self.controller.session.rollback()
            except Exception:
                pass
        finally:
            try:
                self.controller.session.rollback()
            except Exception:
                pass
        
        try:
            total_pages = max(1, (len(self._customers_cache) + self.page_size - 1) // self.page_size)
            self.prev_btn.setEnabled(self.current_page > 0)
            self.next_btn.setEnabled((self.current_page+1) < total_pages)
        except Exception:
            pass

    def on_selection_changed(self):
        """Enable/disable action buttons based on selection"""
        try:
            selected_rows = self.table.selectionModel().selectedRows()
            if selected_rows:
                row = selected_rows[0].row()
                # Get customer ID from the table item
                item = self.table.item(row, 0)
                if item:
                    self.selected_customer_id = item.data(Qt.UserRole)
                    self.edit_customer_btn.setEnabled(True)
                    self.delete_customer_btn.setEnabled(True)
                    self.receive_payment_btn.setEnabled(True)
                    self.statement_btn.setEnabled(True)
                    self.print_btn.setEnabled(True)
                else:
                    self.selected_customer_id = None
                    self.edit_customer_btn.setEnabled(False)
                    self.delete_customer_btn.setEnabled(False)
                    self.receive_payment_btn.setEnabled(False)
                    self.statement_btn.setEnabled(False)
                    self.print_btn.setEnabled(False)
            else:
                self.selected_customer_id = None
                self.edit_customer_btn.setEnabled(False)
                self.delete_customer_btn.setEnabled(False)
                self.receive_payment_btn.setEnabled(False)
                self.statement_btn.setEnabled(False)
                self.print_btn.setEnabled(False)
        except Exception as e:
            print(f"Error in on_selection_changed: {e}")
            # Disable all buttons on error
            try:
                self.edit_customer_btn.setEnabled(False)
                self.delete_customer_btn.setEnabled(False)
                self.receive_payment_btn.setEnabled(False)
                self.statement_btn.setEnabled(False)
                self.print_btn.setEnabled(False)
            except Exception:
                pass

    def edit_selected_customer(self):
        if self.selected_customer_id:
            self._edit_customer(self.selected_customer_id)

    def delete_selected_customer(self):
        if self.selected_customer_id:
            self._delete_customer(self.selected_customer_id)

    def receive_payment_selected(self):
        if self.selected_customer_id:
            self._receive_payment(self.selected_customer_id)

    def statement_selected(self):
        if self.selected_customer_id:
            self._statement(self.selected_customer_id)

    def _delete_customer(self, customer_id):
        res = QMessageBox.question(self, "Confirm", "Delete this customer?", QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            try:
                self.controller.delete_customer(customer_id)
                QMessageBox.information(self, "Deleted", "Customer deleted")
                self.load_customers()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _edit_customer(self, customer_id):
        try:
            from pos_app.models.database import Customer
            cust = self.controller.session.get(Customer, customer_id)
            if not cust:
                QMessageBox.warning(self, "Error", "Customer not found")
                return
            dialog = EditCustomerDialog(self, cust)
            if dialog.exec() == QDialog.Accepted:
                self.controller.update_customer(
                    customer_id,
                    name=dialog.name_input.text().strip(),
                    type=dialog.type_input.currentText().upper(),  # Use string directly
                    contact=dialog.contact_input.text().strip(),
                    email=dialog.email_input.text().strip(),
                    address=dialog.address_input.text().strip(),
                    credit_limit=dialog.credit_limit_input.value()
                )
                QMessageBox.information(self, "Success", "Customer updated")
                self.load_customers()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._update_page()

    def _next_page(self):
        items = self._customers_cache if (self._filtered_customers is None) else (self._filtered_customers or [])
        total_pages = max(1, (len(items) + self.page_size - 1) // self.page_size)
        if (self.current_page+1) < total_pages:
            self.current_page += 1
            self._update_page()

    def _receive_payment(self, customer_id: int):
        # Emit signal for MainWindow to open CustomerPayments page preselected
        try:
            self.action_receive_payment.emit(int(customer_id))
        except Exception:
            pass

    def _statement(self, customer_id: int):
        # Emit signal for MainWindow to export statement
        try:
            self.action_export_statement.emit(int(customer_id))
        except Exception:
            pass
    
    def refresh_customers(self):
        """Refresh the customers list"""
        try:
            print("[Customers] Refreshing customers list...")
            self.load_customers()
            print("[Customers] Customers list refreshed successfully")
        except Exception as e:
            print(f"[Customers] Error refreshing customers: {e}")
            QMessageBox.critical(self, "Error", f"Failed to refresh customers: {str(e)}")
    
    def print_selected_customer(self):
        """Print all customers in table format"""
        try:
            # Show print dialog
            dialog = CustomerPrintDialog(self, None)
            if dialog.exec() == QDialog.Accepted:
                # Get selected printer and print
                printer_name = dialog.get_selected_printer()
                self._do_print_all_customers(printer_name)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to print customers: {str(e)}")
    
    def print_customer_receipt(self, customer_id):
        """Print individual customer receipt with printer selection"""
        try:
            # Show print dialog for printer selection
            dialog = CustomerPrintDialog(self, None)
            dialog.setWindowTitle("Print Customer Receipt")
            # Update info label for receipt
            if hasattr(dialog, 'info_label'):
                dialog.info_label.setText("Print Individual Customer Receipt")
            if dialog.exec() == QDialog.Accepted:
                # Get selected printer and print receipt
                printer_name = dialog.get_selected_printer()
                self._do_print_customer_receipt(customer_id, printer_name)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to print customer receipt: {str(e)}")
    
    def _do_print_customer_receipt(self, customer_id, printer_name):
        """Print individual customer receipt"""
        try:
            from PySide6.QtPrintSupport import QPrinter, QPrinterInfo
            from PySide6.QtGui import QPageSize, QPainter, QFont, QColor, QPageLayout
            from PySide6.QtCore import Qt, QMarginsF
        except ImportError:
            from PyQt6.QtPrintSupport import QPrinter, QPrinterInfo
            from PyQt6.QtGui import QPageSize, QPainter, QFont, QPageLayout
            from PyQt6.QtCore import Qt, QMarginsF
        
        try:
            # Get customer data
            from pos_app.models.database import Customer
            customer = self.controller.session.get(Customer, customer_id)
            if not customer:
                QMessageBox.warning(self, "Error", "Customer not found")
                return
            
            # Create printer
            printer = QPrinter()
            printer.setPageSize(QPageSize(QPageSize.A4))
            printer.setPageOrientation(QPageLayout.Orientation.Portrait)
            printer.setResolution(300)
            
            # Set printer name
            if printer_name and printer_name != "Default":
                printer.setPrinterName(printer_name)
            else:
                printers = QPrinterInfo.availablePrinters()
                if printers:
                    printer.setPrinterName(printers[0].printerName())
            
            # Create painter
            painter = QPainter(printer)
            if not painter.isActive():
                QMessageBox.critical(self, "Print Error", "Failed to initialize printer")
                return
            
            # Get page dimensions
            width = painter.device().width()
            height = painter.device().height()
            
            # Set fonts
            title_font = QFont("Arial", 16, QFont.Bold)
            header_font = QFont("Arial", 12, QFont.Bold)
            normal_font = QFont("Arial", 10)
            
            # Start printing
            y_position = 50
            
            # Store name
            painter.setFont(title_font)
            store_name = "Sarhad General Store"
            painter.drawText(width // 2 - painter.fontMetrics().horizontalAdvance(store_name) // 2, y_position, store_name)
            y_position += 50
            
            # Title
            painter.setFont(header_font)
            title_text = "CUSTOMER RECEIPT"
            painter.drawText(width // 2 - painter.fontMetrics().horizontalAdvance(title_text) // 2, y_position, title_text)
            y_position += 50
            
            # Customer details
            painter.setFont(normal_font)
            customer_type = getattr(customer, 'type', 'RETAIL') or 'RETAIL'
            display_type = customer_type.title() if customer_type else 'Retail'
            details = [
                f"Name: {customer.name or 'N/A'}",
                f"Type: {display_type}",
                f"Contact: {customer.contact or 'N/A'}",
                f"Email: {customer.email or 'N/A'}",
                f"Address: {customer.address or 'N/A'}",
                f"Credit Limit: Rs {customer.credit_limit or 0:,.2f}",
                f"Current Balance: Rs {customer.current_credit or 0:,.2f}"
            ]
            
            for detail in details:
                painter.drawText(50, y_position, detail)
                y_position += 25
            
            # Payment section
            y_position += 20
            painter.setFont(header_font)
            painter.drawText(50, y_position, "Payment Details:")
            y_position += 30
            
            painter.setFont(normal_font)
            painter.drawText(50, y_position, "Amount Paid: _________________")
            y_position += 30
            painter.drawText(50, y_position, "Payment Method: _____________")
            y_position += 30
            painter.drawText(50, y_position, "Signature: ___________________")
            
            # Footer
            y_position = height - 80
            from datetime import datetime
            footer_text = f"Printed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            painter.drawText(width // 2 - painter.fontMetrics().horizontalAdvance(footer_text) // 2, y_position, footer_text)
            
            painter.end()
            QMessageBox.information(self, "Print Complete", "Customer receipt printed successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"Failed to print receipt: {str(e)}")
    
    def _do_print_all_customers(self, printer_name="Default"):
        """Print all customers in table format without dialogs"""
        try:
            from PySide6.QtPrintSupport import QPrinter, QPrinterInfo
            from PySide6.QtGui import QPageSize, QPainter, QFont, QColor, QPageLayout
            from PySide6.QtCore import Qt, QMarginsF
        except ImportError:
            from PyQt6.QtPrintSupport import QPrinter, QPrinterInfo
            from PyQt6.QtGui import QPageSize, QPainter, QFont, QPageLayout
            from PyQt6.QtCore import Qt, QMarginsF
        
        try:
            print("DEBUG: Initializing all customers print...")
            
            # Create printer with legal page size
            try:
                mode_enum = getattr(QPrinter, 'PrinterMode', None)
                if mode_enum is not None:
                    printer = QPrinter(mode_enum.HighResolution)
                else:
                    printer = QPrinter()
            except Exception as e:
                print(f"ERROR creating printer: {e}")
                printer = QPrinter()
            
            # Set legal page size and portrait orientation
            try:
                try:
                    printer.setPageSize(QPageSize(QPageSize.Legal))
                except AttributeError:
                    # Fall back to A4 if Legal is not available
                    printer.setPageSize(QPageSize(QPageSize.A4))
                # Use QPageLayout.Orientation for proper orientation setting
                printer.setPageOrientation(QPageLayout.Orientation.Portrait)
                printer.setResolution(300)
                # Set minimal margins to use full page
                printer.setPageMargins(QMarginsF(2, 2, 2, 2), QPageLayout.Unit.Millimeter)
            except Exception as e:
                print(f"ERROR setting page size: {e}")
                try:
                    # Fallback to A4 if Legal fails
                    printer.setPageSize(QPageSize(QPageSize.A4))
                    printer.setPageOrientation(QPageLayout.Orientation.Portrait)
                    printer.setPageMargins(QMarginsF(2, 2, 2, 2), QPageLayout.Unit.Millimeter)
                except:
                    pass
            
            # Set printer name if specified
            if printer_name and printer_name != "Default":
                printer.setPrinterName(printer_name)
            else:
                # Try to get first available printer
                try:
                    printers = QPrinterInfo.availablePrinters()
                    print(f"DEBUG: Found {len(printers)} printers")
                    
                    if printers:
                        printer.setPrinterName(printers[0].printerName())
                        print(f"DEBUG: Using printer: {printers[0].printerName()}")
                    else:
                        QMessageBox.warning(self, "No Printer", 
                            "No printer found. Please install a printer and try again.")
                        return
                except Exception as e:
                    print(f"ERROR getting printer info: {e}")
                    QMessageBox.critical(self, "Printer Error", 
                        f"Failed to access printer information: {str(e)}")
                    return
            
            print("DEBUG: Starting all customers print...")
            
            # Create painter and draw content
            painter = QPainter(printer)
            if not painter.isActive():
                print("ERROR: Painter failed to start")
                QMessageBox.critical(self, "Print Error", "Failed to initialize printer. Please check your printer connection.")
                return
                
            try:
                painter.setRenderHint(QPainter.Antialiasing)
            except AttributeError:
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Get page dimensions from printer's printable area
            try:
                page_rect = printer.pageRect(QPrinter.DevicePixel)
                width = page_rect.width()
                height = page_rect.height()
                print(f"DEBUG: Printable area: {width}x{height}")
            except Exception:
                # Fallback to device dimensions
                width = painter.device().width()
                height = painter.device().height()
                print(f"DEBUG: Using device dimensions: {width}x{height}")
            
            print(f"DEBUG: Page dimensions: {width}x{height}")
            print(f"DEBUG: Printer resolution: {printer.resolution()}")
            
            # Calculate DPI scaling factor - fix for printer resolution
            dpi = printer.resolution()
            # Use fixed scale to prevent microscopic text on high DPI printers
            scale = max(1.0, min(dpi / 72.0, 3.0))  # Clamp between 1.0 and 3.0
            print(f"[DEBUG] Printer DPI: {dpi}, Scale: {scale}")
            
            # Use fixed font sizes that work regardless of printer DPI
            store_font = QFont("Arial", 24, QFont.Bold)  # H1 heading - larger and bolder
            title_font = QFont("Arial", 12, QFont.Bold)
            header_font = QFont("Arial", 10, QFont.Bold)
            normal_font = QFont("Arial", 9)
            
            # Use reasonable margins with proper top spacing
            margin = 50  # Fixed 50 pixel margin
            top_space = 100  # Fixed 100 pixels from top for header
            left_margin = margin
            right_margin = width - margin
            y_position = top_space  # Start 100 pixels from top
            
            # Store Name with light gray background
            painter.setFont(store_font)
            store_name = "Sarhad General Store"
            store_width = painter.fontMetrics().horizontalAdvance(store_name)
            store_height = painter.fontMetrics().height()
            # Draw light gray background box
            store_box_width = width - 2 * margin  # Full width minus margins
            store_box_height = store_height + 40  # Height with padding
            store_box_x = margin
            store_box_y = y_position - 20
            painter.fillRect(store_box_x, store_box_y, store_box_width, store_box_height, QColor(240, 240, 240))  # Very light gray
            painter.drawRect(store_box_x, store_box_y, store_box_width, store_box_height)
            # Center the text horizontally and vertically in the box
            text_x = width // 2 - store_width // 2
            text_y = store_box_y + (store_box_height + store_height) // 2 - 5
            painter.drawText(text_x, text_y, store_name)
            y_position += store_box_height + 30
            
            # Title with center alignment
            painter.setFont(title_font)
            title_text = "CUSTOMER LIST"
            title_width = painter.fontMetrics().horizontalAdvance(title_text)
            title_height = painter.fontMetrics().height()
            # Center the title horizontally and vertically
            title_box_width = title_width + 60
            title_box_height = title_height + 40
            title_box_x = width // 2 - title_box_width // 2
            title_box_y = y_position - 20
            painter.drawRect(title_box_x, title_box_y, title_box_width, title_box_height)
            text_x = width // 2 - title_width // 2
            text_y = title_box_y + (title_box_height + title_height) // 2 - 5
            painter.drawText(text_x, text_y, title_text)
            y_position += title_box_height + 50  # Increased spacing from 30 to 50 for one line space
            
            # Table headers - Update column names for clarity
            painter.setFont(header_font)
            headers = ["Name", "Previous Balance", "Last Payment", "Balance Due", "Now Paid"]
            
            # Calculate column positions with proportional widths
            usable_width = right_margin - left_margin
            # Name: 30%, Previous Balance: 17.5%, Last Payment: 17.5%, Balance Due: 17.5%, Now Paid: 17.5%
            col_widths = [
                usable_width * 0.30,   # Name
                usable_width * 0.175,  # Previous Balance
                usable_width * 0.175,  # Last Payment
                usable_width * 0.175,  # Balance Due
                usable_width * 0.175   # Now Paid
            ]
            
            x_positions = [left_margin]
            for i in range(len(col_widths)):
                if i < len(col_widths) - 1:
                    x_positions.append(x_positions[-1] + col_widths[i])
            
            print(f"DEBUG: Column positions: {x_positions}")
            print(f"DEBUG: Column widths: {col_widths}")
            
            # Draw headers with light background (full width) - center aligned
            header_box_height = 100
            # Draw light background for entire header row
            try:
                from PySide6.QtGui import QColor
            except ImportError:
                from PyQt6.QtGui import QColor
            painter.fillRect(int(left_margin), y_position - 25, int(right_margin - left_margin), header_box_height, QColor(230, 230, 230))  # Light gray background
            painter.drawRect(int(left_margin), y_position - 25, int(right_margin - left_margin), header_box_height)  # Border around entire header
            
            for i, header in enumerate(headers):
                # Center text horizontally within the cell
                header_width = painter.fontMetrics().horizontalAdvance(header)
                text_x = int(x_positions[i]) + (int(col_widths[i]) - header_width) // 2
                text_y = y_position
                painter.drawText(text_x, text_y, header)
                # Draw vertical grid lines between columns
                if i < len(headers) - 1:
                    painter.drawLine(int(x_positions[i+1]), y_position - 25, int(x_positions[i+1]), y_position + 15)
            y_position += 50
            
            # Draw horizontal line under headers
            painter.drawLine(int(left_margin), y_position, int(right_margin), y_position)
            y_position += 40
            
            # Get ALL customers from database and SORT by balance descending
            try:
                from pos_app.models.database import Customer
                all_customers = self.controller.session.query(Customer).filter(Customer.is_active == True).all()
                if not all_customers:
                    # Try without the is_active filter
                    all_customers = self.controller.session.query(Customer).all()
                
                # Sort by current_credit (balance) descending - highest balances first
                all_customers = sorted(all_customers, key=lambda c: getattr(c, 'current_credit', 0.0) or 0.0, reverse=True)
                print(f"DEBUG: Found {len(all_customers)} customers in database (sorted by balance)")
            except Exception as e:
                print(f"ERROR querying customers: {e}")
                all_customers = []
            
            # Table data with grid lines and zebra striping
            painter.setFont(normal_font)
            # Calculate dynamic row height based on font size
            font_metrics = painter.fontMetrics()
            row_height = font_metrics.height() + 40  # Increased padding to prevent text overlap on lines
            header_footer_space = 400  # Space for header, footer, and totals
            max_rows_per_page = (height - header_footer_space) // row_height
            current_row = 0
            
            # Track totals for summary
            total_previous_balance = 0.0
            total_last_paid = 0.0
            total_new_balance = 0.0
            
            print(f"DEBUG: Total customers to print: {len(all_customers)}")
            print(f"DEBUG: Max rows per page: {max_rows_per_page}")
            
            for idx, customer in enumerate(all_customers):
                # Check if we need a new page BEFORE drawing current customer
                # Only create new page if this isn't the last customer
                if current_row >= max_rows_per_page and idx < len(all_customers) - 1:
                    print(f"DEBUG: Starting new page after customer {idx-1}")
                    printer.newPage()
                    # Reset y_position to account for header space
                    y_position = margin + 100  # Account for header height
                    current_row = 0
                    
                    # Repeat headers on new page with proper formatting
                    painter.setFont(header_font)
                    header_box_height = 40
                    # Draw light background for entire header row
                    painter.fillRect(int(left_margin), y_position - 25, int(right_margin - left_margin), header_box_height, QColor(230, 230, 230))  # Light gray background
                    painter.drawRect(int(left_margin), y_position - 25, int(right_margin - left_margin), header_box_height)  # Border around entire header
                    
                    for i, header in enumerate(headers):
                        # Center text horizontally within cell
                        header_width = painter.fontMetrics().horizontalAdvance(header)
                        text_x = int(x_positions[i]) + (int(col_widths[i]) - header_width) // 2
                        text_y = y_position
                        painter.drawText(text_x, text_y, header)
                        # Draw vertical grid lines between columns
                        if i < len(headers) - 1:
                            painter.drawLine(int(x_positions[i+1]), y_position - 25, int(x_positions[i+1]), y_position + 15)
                    y_position += 50
                    
                    # Draw horizontal line under headers
                    painter.drawLine(int(left_margin), y_position, int(right_margin), y_position)
                    y_position += 40
                    painter.setFont(normal_font)
                
                # Get customer data from database object
                try:
                    customer_name = getattr(customer, 'name', 'Unknown') or 'Unknown'
                    print(f"DEBUG: Processing customer {idx}: {customer_name}")
                    customer_id = getattr(customer, 'id', None)
                    
                    if customer:
                        # New Balance: Current outstanding balance (what customer owes now)
                        new_balance = getattr(customer, 'current_credit', 0.0) or 0.0
                        
                        # Calculate Total Sales for this customer (actual invoiced amount)
                        try:
                            from pos_app.models.database import Sale, Payment
                            from sqlalchemy import func
                            # Get SUM of all sales (total invoice amounts, excluding refunds)
                            # We want to show the gross sales before any refunds
                            gross_sales = self.controller.session.query(func.sum(Sale.total_amount))\
                                .filter(Sale.customer_id == customer_id)\
                                .filter(or_(Sale.status == 'COMPLETED', Sale.status == 'REFUNDED'))\
                                .filter(Sale.is_refund != True)\
                                .scalar()
                            total_sales = gross_sales if gross_sales is not None else 0.0
                        except Exception as e:
                            print(f"Error fetching total sales: {e}")
                            total_sales = 0.0
                        
                        # Last Paid: Get the MOST RECENT payment amount (not total)
                        try:
                            # Get the most recent actual payment (exclude CREDIT bookkeeping)
                            recent_payment = self.controller.session.query(Payment.amount)\
                                .filter(Payment.customer_id == customer_id)\
                                .filter(Payment.amount > 0)\
                                .filter(Payment.payment_method != 'CREDIT')\
                                .order_by(Payment.payment_date.desc())\
                                .first()
                            last_paid = recent_payment[0] if recent_payment and recent_payment[0] is not None else 0.0
                        except Exception as e:
                            print(f"Error fetching recent payment: {e}")
                            last_paid = 0.0
                        
                        # Previous Balance: Calculate as Balance Due + Last Payment
                        # This shows what the balance was before the last payment
                        previous_balance = new_balance + last_paid
                    else:
                        previous_balance = 0.0
                        last_paid = 0.0
                        new_balance = 0.0
                    
                    print(f"DEBUG: Customer {idx}: Name={customer_name}, Previous Balance={previous_balance}, Last Paid={last_paid}, New Balance={new_balance}")
                except Exception as e:
                    print(f"ERROR reading customer {idx}: {e}")
                    continue
                
                # Add to totals
                total_previous_balance += previous_balance
                total_last_paid += last_paid
                total_new_balance += new_balance
                
                # Zebra striping - alternating row colors
                if idx % 2 == 0:
                    # Light gray background for even rows
                    try:
                        from PySide6.QtGui import QColor
                    except ImportError:
                        from PyQt6.QtGui import QColor
                    painter.fillRect(int(x_positions[0]), y_position, int(right_margin - left_margin), row_height, QColor(245, 245, 245))
                
                # Draw customer data with boxes - CENTER align ALL columns
                # Column 1: Name - center aligned
                max_name_width = col_widths[0] - 20
                truncated_name = customer_name
                while painter.fontMetrics().horizontalAdvance(truncated_name) > max_name_width and len(truncated_name) > 3:
                    truncated_name = truncated_name[:-1]
                painter.drawRect(int(x_positions[0]), y_position, int(col_widths[0]), row_height)
                text_width = painter.fontMetrics().horizontalAdvance(truncated_name)
                text_x = int(x_positions[0]) + (int(col_widths[0]) - text_width) // 2  # Center align
                text_y = y_position + (row_height + painter.fontMetrics().height()) // 2 - 3  # Better vertical centering
                painter.drawText(text_x, text_y, truncated_name)
                
                # Column 2: Previous Balance - CENTER aligned
                balance_text = f"{previous_balance:.2f}"
                painter.drawRect(int(x_positions[1]), y_position, int(col_widths[1]), row_height)
                text_width = painter.fontMetrics().horizontalAdvance(balance_text)
                text_x = int(x_positions[1]) + (int(col_widths[1]) - text_width) // 2  # Center align
                text_y = y_position + (row_height + painter.fontMetrics().height()) // 2 - 3  # Better vertical centering
                painter.drawText(text_x, text_y, balance_text)
                
                # Column 3: Last Payment - CENTER aligned
                last_paid_text = f"{last_paid:.2f}"
                painter.drawRect(int(x_positions[2]), y_position, int(col_widths[2]), row_height)
                text_width = painter.fontMetrics().horizontalAdvance(last_paid_text)
                text_x = int(x_positions[2]) + (int(col_widths[2]) - text_width) // 2  # Center align
                text_y = y_position + (row_height + painter.fontMetrics().height()) // 2 - 3  # Better vertical centering
                painter.drawText(text_x, text_y, last_paid_text)
                
                # Column 4: Balance Due - CENTER aligned with RED color for negatives
                new_balance_text = f"{new_balance:.2f}"
                painter.drawRect(int(x_positions[3]), y_position, int(col_widths[3]), row_height)
                
                # Highlight negative balances in RED
                if new_balance < 0:
                    try:
                        from PySide6.QtGui import QColor
                    except ImportError:
                        from PyQt6.QtGui import QColor
                    painter.setPen(QColor(220, 38, 38))  # Red color
                    new_balance_text = f"({abs(new_balance):.2f})"  # Use parentheses for negatives
                
                text_width = painter.fontMetrics().horizontalAdvance(new_balance_text)
                text_x = int(x_positions[3]) + (int(col_widths[3]) - text_width) // 2  # Center align
                text_y = y_position + (row_height + painter.fontMetrics().height()) // 2 - 3  # Better vertical centering
                painter.drawText(text_x, text_y, new_balance_text)
                
                # Reset pen color to black
                try:
                    from PySide6.QtGui import QColor
                except ImportError:
                    from PyQt6.QtGui import QColor
                painter.setPen(QColor(0, 0, 0))
                
                # Column 5: Now Paid (empty for manual entry) - CENTER aligned
                now_paid_text = ""
                painter.drawRect(int(x_positions[4]), y_position, int(col_widths[4]), row_height)
                text_width = painter.fontMetrics().horizontalAdvance(now_paid_text)
                text_x = int(x_positions[4]) + (int(col_widths[4]) - text_width) // 2  # Center align
                text_y = y_position + (row_height + painter.fontMetrics().height()) // 2 - 3
                painter.drawText(text_x, text_y, now_paid_text)
                
                y_position += row_height
                current_row += 1
                
                print(f"DEBUG: Successfully printed customer {idx}: {customer_name}")
            
            # Add summary totals row
            y_position += 20  # Extra space before totals
            painter.setFont(header_font)
            
            # Draw totals row with bold text and boxes
            try:
                from PySide6.QtGui import QColor
            except ImportError:
                from PyQt6.QtGui import QColor
            
            # Light blue background for totals row
            painter.fillRect(int(x_positions[0]), y_position, int(right_margin - left_margin), row_height, QColor(220, 240, 255))
            
            # "TOTALS" label - CENTER aligned
            painter.drawRect(int(x_positions[0]), y_position, int(col_widths[0]), row_height)
            text_width = painter.fontMetrics().horizontalAdvance("TOTALS")
            text_x = int(x_positions[0]) + (int(col_widths[0]) - text_width) // 2  # Center align
            text_y = y_position + (row_height + painter.fontMetrics().height()) // 2 - 3  # Better vertical centering
            painter.drawText(text_x, text_y, "TOTALS")
            
            # Total Previous Balance - CENTER aligned
            total_prev_text = f"{total_previous_balance:.2f}"
            painter.drawRect(int(x_positions[1]), y_position, int(col_widths[1]), row_height)
            text_width = painter.fontMetrics().horizontalAdvance(total_prev_text)
            text_x = int(x_positions[1]) + (int(col_widths[1]) - text_width) // 2  # Center align
            painter.drawText(text_x, text_y, total_prev_text)
            
            # Total of Last Payments - For reference only
            total_paid_text = f"{total_last_paid:.2f}"
            painter.drawRect(int(x_positions[2]), y_position, int(col_widths[2]), row_height)
            text_width = painter.fontMetrics().horizontalAdvance(total_paid_text)
            text_x = int(x_positions[2]) + (int(col_widths[2]) - text_width) // 2  # Center align
            painter.drawText(text_x, text_y, total_paid_text)
            
            # Total Balance Due - CENTER aligned (with red if negative)
            total_new_text = f"{total_new_balance:.2f}"
            if total_new_balance < 0:
                painter.setPen(QColor(220, 38, 38))
                total_new_text = f"({abs(total_new_balance):.2f})"
            painter.drawRect(int(x_positions[3]), y_position, int(col_widths[3]), row_height)
            text_width = painter.fontMetrics().horizontalAdvance(total_new_text)
            text_x = int(x_positions[3]) + (int(col_widths[3]) - text_width) // 2  # Center align
            painter.drawText(text_x, text_y, total_new_text)
            painter.setPen(QColor(0, 0, 0))  # Reset to black
            
            # Now Paid column in totals (empty)
            painter.drawRect(int(x_positions[4]), y_position, int(col_widths[4]), row_height)
            
            # Footer - center aligned
            painter.setFont(normal_font)
            from datetime import datetime
            footer_text = f"Printed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Customers: {len(all_customers)}"
            footer_width = painter.fontMetrics().horizontalAdvance(footer_text)
            footer_x = width // 2 - footer_width // 2
            painter.drawText(footer_x, height - 40, footer_text)
            
            painter.end()
            print("DEBUG: All customers print completed successfully")
            QMessageBox.information(self, "Print Complete", f"Printed {len(all_customers)} customers successfully!")
            
        except Exception as e:
            print(f"ERROR in _do_print_all_customers: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Print Error", f"Failed to print customers: {str(e)}")


class CustomerPrintDialog(QDialog):
    def __init__(self, parent=None, customers=None):
        super().__init__(parent)
        self.setWindowTitle("Print Customer List")
        self.setModal(True)
        self.resize(400, 200)
        self.customers = customers
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Select Printer")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Printer selection
        self.printer_combo = QComboBox()
        try:
            from PySide6.QtPrintSupport import QPrinterInfo
        except ImportError:
            from PyQt6.QtPrintSupport import QPrinterInfo
            
        printers = QPrinterInfo.availablePrinters()
        self.printer_combo.addItem("Default Printer")
        for printer in printers:
            self.printer_combo.addItem(printer.printerName())
        
        layout.addWidget(self.printer_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        print_btn = QPushButton("Print")
        print_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(print_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def get_selected_printer(self):
        index = self.printer_combo.currentIndex()
        if index == 0:
            return "Default"
        else:
            return self.printer_combo.currentText()


class CustomerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Customer")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.type_input = QComboBox()
        self.type_input.addItems(["Retail", "Wholesale"])
        self.contact_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QLineEdit()
        self.credit_limit_input = QDoubleSpinBox()
        self.credit_limit_input.setMaximum(10000000.00)
        self.credit_limit_input.setDecimals(2)

        layout.addRow("Name:", self.name_input)
        layout.addRow("Type:", self.type_input)
        layout.addRow("Contact:", self.contact_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Address:", self.address_input)
        layout.addRow("Credit Limit:", self.credit_limit_input)

        buttons = QHBoxLayout()
        ok_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addRow(buttons)


class EditCustomerDialog(CustomerDialog):
    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Customer")
        self.customer = customer
        if customer:
            self.name_input.setText(customer.name or "")
            try:
                customer_type = str(customer.type).title() if customer.type else "Retail"
                self.type_input.setCurrentText(customer_type)
            except Exception:
                pass
            self.contact_input.setText(customer.contact or "")
            self.email_input.setText(customer.email or "")
            self.address_input.setText(customer.address or "")
            self.credit_limit_input.setValue(customer.credit_limit or 0.0)


class CustomerPrintDialog(QDialog):
    """Dialog for selecting printer and print options"""
    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.setWindowTitle("Print Customers")
        self.customer = customer
        self.selected_printer = "Default"
        self.setup_ui()
    
    def setup_ui(self):
        layout = QFormLayout(self)
        
        # Title
        info_label = QLabel("Print All Customers Report")
        info_label.setStyleSheet("font-weight: bold; color: #60a5fa; font-size: 12px;")
        layout.addRow(info_label)
        
        # Printer selection
        self.printer_combo = QComboBox()
        self.printer_combo.addItem("Default Printer", "Default")
        
        # Try to get available printers
        try:
            from PySide6.QtPrintSupport import QPrinterInfo
        except ImportError:
            from PyQt6.QtPrintSupport import QPrinterInfo
        
        try:
            printers = QPrinterInfo.availablePrinters()
            for printer in printers:
                printer_name = printer.printerName()
                self.printer_combo.addItem(printer_name, printer_name)
        except Exception as e:
            print(f"Could not load printers: {e}")
        
        layout.addRow("Select Printer:", self.printer_combo)
        
        # Paper size info
        paper_info = QLabel("Paper Size: A4 (Landscape)")
        paper_info.setStyleSheet("color: #94a3b8; font-size: 10px;")
        layout.addRow(paper_info)
        
        # Print content info
        content_label = QLabel("Will print table with: Name, Phone, Email, Type, Credit Limit, Balance, Payment (blank for manual entry)")
        content_label.setStyleSheet("color: #94a3b8; font-size: 10px;")
        content_label.setWordWrap(True)
        layout.addRow(content_label)
        
        # Buttons
        buttons = QHBoxLayout()
        ok_button = QPushButton("🖨️ Print")
        ok_button.setProperty('accent', 'Qt.green')
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addRow(buttons)
    
    def get_selected_printer(self):
        """Get the selected printer name"""
        return self.printer_combo.currentData()
