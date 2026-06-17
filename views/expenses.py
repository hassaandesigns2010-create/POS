try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
        QDialog, QFormLayout, QLineEdit, QMessageBox, QHBoxLayout, QComboBox,
        QCheckBox, QSpinBox, QGroupBox, QTabWidget, QDateEdit
    )
    from PySide6.QtCore import QDate, QTimer
except ImportError:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
        QDialog, QFormLayout, QLineEdit, QMessageBox, QHBoxLayout, QComboBox,
        QCheckBox, QSpinBox, QGroupBox, QTabWidget, QDateEdit
    )
    from PyQt6.QtCore import QDate, QTimer
from datetime import datetime, timedelta
from pos_app.models.database import Expense
from pos_app.utils.document_generator import DocumentGenerator


def parse_frequency_from_notes(notes):
    """Parse frequency from ExpenseSchedule notes field"""
    if not notes:
        return "Monthly"  # Default
    notes_upper = notes.upper()
    if "WEEKLY" in notes_upper:
        return "Weekly"
    elif "DAILY" in notes_upper:
        return "Daily"
    elif "YEARLY" in notes_upper:
        return "Yearly"
    elif "QUARTERLY" in notes_upper:
        return "Quarterly"
    elif "MONTHLY" in notes_upper:
        return "Monthly"
    return "Monthly"  # Default


class CreateRecurringExpenseDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Setup Recurring Expense")
        layout = QFormLayout(self)

        self.title_input = QLineEdit()
        self.amount_input = QLineEdit()
        self.category_input = QLineEdit()

        # Recurring options
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"])

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addYears(1))

        self.auto_create = QCheckBox("Automatically create expenses")
        self.auto_create.setChecked(True)

        layout.addRow("Title:", self.title_input)
        layout.addRow("Amount:", self.amount_input)
        layout.addRow("Category:", self.category_input)
        layout.addRow("Frequency:", self.frequency_combo)
        layout.addRow("Start Date:", self.start_date)
        layout.addRow("End Date:", self.end_date)
        layout.addRow(self.auto_create)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Recurring")
        cancel_btn = QPushButton("Cancel")

        save_btn.clicked.connect(self.save_recurring)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def save_recurring(self):
        try:
            title = self.title_input.text()
            try:
                amount = float(self.amount_input.text())
            except (ValueError, TypeError):
                amount = 0.0
            category = self.category_input.text() or None
            frequency = self.frequency_combo.currentText()
            # PySide6 uses toPython(), PyQt6 uses toPyDate()
            try:
                start_date = self.start_date.date().toPython()
                end_date = self.end_date.date().toPython()
            except AttributeError:
                start_date = self.start_date.date().toPyDate()
                end_date = self.end_date.date().toPyDate()
            auto_create = self.auto_create.isChecked()

            recurring = self.controller.create_recurring_expense(
                title, amount, category, frequency, start_date, end_date, auto_create
            )
            QMessageBox.information(self, "Saved", f"Recurring expense setup: {title}")
            self.accept()
        except Exception as exc:
            QMessageBox.warning(self, "Error", str(exc))


class EditRecurringExpenseDialog(QDialog):
    def __init__(self, controller, recurring_expense, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.recurring_expense = recurring_expense
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Edit Recurring Expense")
        layout = QFormLayout(self)

        # ExpenseSchedule doesn't have title/category fields directly
        # Parse them from notes field (format: "category - frequency" or just "frequency")
        notes = self.recurring_expense.notes or ""
        category = ""
        if " - " in notes:
            parts = notes.split(" - ", 1)
            category = parts[0]
            title = parts[1] if len(parts) > 1 else notes
        else:
            title = notes

        self.title_input = QLineEdit(title)
        self.amount_input = QLineEdit(str(self.recurring_expense.amount))
        self.category_input = QLineEdit(category)

        # Recurring options
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"])
        self.frequency_combo.setCurrentText(parse_frequency_from_notes(self.recurring_expense.notes))

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        # Expense uses next_due_date, not start_date
        if hasattr(self.recurring_expense, 'next_due_date') and self.recurring_expense.next_due_date:
            self.start_date.setDate(self.recurring_expense.next_due_date)
        else:
            self.start_date.setDate(QDate.currentDate())

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        # ExpenseSchedule doesn't have end_date, use default
        self.end_date.setDate(QDate.currentDate().addYears(1))

        self.auto_create = QCheckBox("Automatically create expenses")
        self.auto_create.setChecked(False)  # ExpenseSchedule doesn't have auto_create field

        layout.addRow("Title:", self.title_input)
        layout.addRow("Amount:", self.amount_input)
        layout.addRow("Category:", self.category_input)
        layout.addRow("Frequency:", self.frequency_combo)
        layout.addRow("Start Date:", self.start_date)
        layout.addRow("End Date:", self.end_date)
        layout.addRow(self.auto_create)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Update Recurring")
        cancel_btn = QPushButton("Cancel")

        save_btn.clicked.connect(self.update_recurring)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def update_recurring(self):
        try:
            title = self.title_input.text()
            try:
                amount = float(self.amount_input.text())
            except (ValueError, TypeError):
                amount = 0.0
            category = self.category_input.text() or None
            frequency = self.frequency_combo.currentText()
            start_date = self.start_date.date().toPython()
            end_date = self.end_date.date().toPython()
            auto_create = self.auto_create.isChecked()

            updated = self.controller.update_recurring_expense(
                str(self.recurring_expense.id), title, amount, category,
                frequency, start_date, end_date, auto_create
            )
            QMessageBox.information(self, "Updated", f"Recurring expense updated: {title}")
            self.accept()
        except Exception as exc:
            QMessageBox.warning(self, "Error", str(exc))


class CreateExpenseDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Record Expense")
        layout = QFormLayout(self)
        self.title_input = QLineEdit()
        self.amount_input = QLineEdit()
        self.category_input = QLineEdit()
        layout.addRow("Title:", self.title_input)
        layout.addRow("Amount:", self.amount_input)
        layout.addRow("Category:", self.category_input)
        btn = QPushButton("Save")
        btn.clicked.connect(self.save_expense)
        layout.addRow(btn)

    def save_expense(self):
        try:
            title = self.title_input.text()
            try:
                amount = float(self.amount_input.text())
            except (ValueError, TypeError):
                amount = 0.0
            category = self.category_input.text() or None
            e = self.controller.add_expense(title, amount, category)
            QMessageBox.information(self, "Saved", f"Expense recorded: Rs {e.amount:,.2f}")
            self.accept()
        except Exception as exc:
            QMessageBox.warning(self, "Error", str(exc))


class CreateStandardExpenseDialog(QDialog):
    """Dialog to create a new standard expense account (like Ali, Food, Rent)"""
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Create Standard Expense Account")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.category_input = QLineEdit()
        self.description_input = QLineEdit()

        layout.addRow("Name:", self.name_input)
        layout.addRow("Category:", self.category_input)
        layout.addRow("Description:", self.description_input)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")

        self.save_btn.clicked.connect(self.save_standard_expense)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def save_standard_expense(self):
        try:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Error", "Name is required")
                return

            category = self.category_input.text().strip() or None
            description = self.description_input.text().strip() or None

            self.controller.create_standard_expense(name, category, description)
            QMessageBox.information(self, "Saved", f"Standard expense account '{name}' created")
            self.accept()
        except Exception as exc:
            QMessageBox.warning(self, "Error", str(exc))


class PayStandardExpenseDialog(QDialog):
    """Dialog to pay against a standard expense account"""
    def __init__(self, standard_expense, controller, parent=None):
        super().__init__(parent)
        self.standard_expense = standard_expense
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"Pay {self.standard_expense.name}")
        self.setMinimumWidth(350)
        layout = QFormLayout(self)

        # Show account info
        info_label = QLabel(f"<b>Account:</b> {self.standard_expense.name}<br>"
                           f"<b>Category:</b> {self.standard_expense.category or 'N/A'}")
        layout.addRow(info_label)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount to pay")

        self.payment_method = QComboBox()
        self.payment_method.addItems(["CASH", "BANK_TRANSFER", "CREDIT_CARD", "DEBIT_CARD"])

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Optional notes")

        layout.addRow("Amount (Rs):", self.amount_input)
        layout.addRow("Payment Method:", self.payment_method)
        layout.addRow("Notes:", self.notes_input)

        btn_layout = QHBoxLayout()
        pay_btn = QPushButton("Pay")
        cancel_btn = QPushButton("Cancel")

        pay_btn.clicked.connect(self.process_payment)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(pay_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def process_payment(self):
        try:
            try:
                amount = float(self.amount_input.text())
                if amount <= 0:
                    QMessageBox.warning(self, "Error", "Amount must be greater than 0")
                    return
            except (ValueError, TypeError):
                QMessageBox.warning(self, "Error", "Please enter a valid amount")
                return

            payment_method = self.payment_method.currentText()
            notes = self.notes_input.text().strip() or None

            expense = self.controller.pay_standard_expense(
                self.standard_expense.id,
                amount,
                payment_method,
                notes
            )
            QMessageBox.information(self, "Payment Successful", 
                                   f"Paid Rs {amount:,.2f} for {self.standard_expense.name}")
            self.accept()
        except Exception as exc:
            QMessageBox.warning(self, "Error", str(exc))


class ExpensesWidget(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        # Ensure clean transaction state before loading data
        try:
            self.controller.session.rollback()
        except Exception as e:
            pass
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("📉 Expenses")
        header.setProperty('role', 'heading')
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #f8fafc;")
        layout.addWidget(header)

        # Toolbar with tabs
        toolbar = QHBoxLayout()

        # Create tabs
        self.tabs = QTabWidget()

        # Regular Expenses Tab
        self.expenses_tab = QWidget()
        self.setup_expenses_tab()
        self.tabs.addTab(self.expenses_tab, "Regular Expenses")

        # Standard Expenses Tab
        self.standard_tab = QWidget()
        self.setup_standard_tab()
        self.tabs.addTab(self.standard_tab, "Standard Expenses")

        # Recurring Expenses Tab
        self.recurring_tab = QWidget()
        self.setup_recurring_tab()
        self.tabs.addTab(self.recurring_tab, "Recurring Expenses")

        layout.addWidget(self.tabs)

    def setup_expenses_tab(self):
        layout = QVBoxLayout(self.expenses_tab)

        # Toolbar for regular expenses
        toolbar = QHBoxLayout()
        add_btn = QPushButton("✨ New Expense")
        add_btn.clicked.connect(self.open_create_expense)
        toolbar.addWidget(add_btn)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())  # Show today only by default
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())  # Show today only by default
        toolbar.addWidget(QLabel("From:"))
        toolbar.addWidget(self.start_date)
        toolbar.addWidget(QLabel("To:"))
        toolbar.addWidget(self.end_date)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_expenses)
        toolbar.addWidget(refresh_btn)

        export_btn = QPushButton("📄 Export CSV")
        export_btn.clicked.connect(self.export_csv)
        toolbar.addWidget(export_btn)

        layout.addLayout(toolbar)

        # Regular expenses table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Title", "Amount", "Category", "Date"])
        layout.addWidget(self.table)
        self.load_expenses()

    def setup_recurring_tab(self):
        layout = QVBoxLayout(self.recurring_tab)

        # Toolbar for recurring expenses
        toolbar = QHBoxLayout()
        add_btn = QPushButton("➕ New Recurring")
        add_btn.clicked.connect(self.open_create_recurring)
        toolbar.addWidget(add_btn)

        # Add refresh button for recurring expenses too
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_recurring_expenses)
        toolbar.addWidget(refresh_btn)

        process_btn = QPushButton("⚡ Process Due")
        process_btn.clicked.connect(self.process_recurring_expenses)
        toolbar.addWidget(process_btn)

        layout.addLayout(toolbar)

        # Recurring expenses table
        self.recurring_table = QTableWidget(0, 6)
        self.recurring_table.setHorizontalHeaderLabels(["Title", "Amount", "Frequency", "Next Due", "Auto Create", "Actions"])
        layout.addWidget(self.recurring_table)
        self.load_recurring_expenses()

    def setup_standard_tab(self):
        """Setup the Standard Expenses tab with Pay button in toolbar"""
        layout = QVBoxLayout(self.standard_tab)

        # Toolbar for standard expenses
        toolbar = QHBoxLayout()
        
        add_btn = QPushButton("➕ New Standard Expense")
        add_btn.clicked.connect(self.open_create_standard_expense)
        toolbar.addWidget(add_btn)

        # Pay button in toolbar - user selects row first, then clicks Pay
        self.pay_btn = QPushButton("💰 Pay")
        self.pay_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.pay_btn.clicked.connect(self.pay_selected_standard_expense)
        toolbar.addWidget(self.pay_btn)

        # Add refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_standard_expenses)
        toolbar.addWidget(refresh_btn)

        layout.addLayout(toolbar)

        # Standard expenses table (no action buttons in rows)
        self.standard_table = QTableWidget(0, 4)
        self.standard_table.setHorizontalHeaderLabels(["Name", "Category", "Description", "Status"])
        self.standard_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.standard_table.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.standard_table)
        self.load_standard_expenses()

    def load_standard_expenses(self):
        """Load standard expense accounts into the table"""
        try:
            standard_expenses = self.controller.list_standard_expenses()
            self.standard_table.setRowCount(len(standard_expenses))

            for i, exp in enumerate(standard_expenses):
                self.standard_table.setItem(i, 0, QTableWidgetItem(exp.name))
                self.standard_table.setItem(i, 1, QTableWidgetItem(exp.category or ""))
                self.standard_table.setItem(i, 2, QTableWidgetItem(exp.description or ""))
                self.standard_table.setItem(i, 3, QTableWidgetItem("Active" if exp.is_active else "Inactive"))
        except Exception as e:
            print(f"Error loading standard expenses: {e}")
            try:
                self.controller.session.rollback()
            except Exception:
                pass
            self.standard_table.setRowCount(0)

    def open_create_standard_expense(self):
        """Open dialog to create a new standard expense account"""
        dlg = CreateStandardExpenseDialog(self.controller, self)
        if dlg.exec() == QDialog.Accepted:
            self.load_standard_expenses()

    def pay_selected_standard_expense(self):
        """Pay the selected standard expense from the toolbar button"""
        try:
            selected_row = self.standard_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "No Selection", "Please select a standard expense account first")
                return
            
            # Get the expense at the selected row
            standard_expenses = self.controller.list_standard_expenses()
            if selected_row >= len(standard_expenses):
                QMessageBox.warning(self, "Error", "Invalid selection")
                return
            
            standard = standard_expenses[selected_row]
            dlg = PayStandardExpenseDialog(standard, self.controller, self)
            if dlg.exec() == QDialog.Accepted:
                QMessageBox.information(self, "Success", f"Payment recorded for {standard.name}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to process payment: {str(e)}")

    def edit_standard_expense(self):
        """Edit the selected standard expense account (double-click or context menu)"""
        try:
            selected_row = self.standard_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "No Selection", "Please select a standard expense account first")
                return
            
            standard_expenses = self.controller.list_standard_expenses()
            if selected_row >= len(standard_expenses):
                return
            
            standard = standard_expenses[selected_row]
            # Create and open edit dialog
            dlg = CreateStandardExpenseDialog(self.controller, self)
            dlg.setWindowTitle("Edit Standard Expense Account")
            dlg.name_input.setText(standard.name)
            dlg.category_input.setText(standard.category or "")
            dlg.description_input.setText(standard.description or "")
            
            # Override save method to update instead of create
            def update_expense():
                try:
                    name = dlg.name_input.text().strip()
                    if not name:
                        QMessageBox.warning(dlg, "Error", "Name is required")
                        return
                    
                    self.controller.update_standard_expense(
                        standard.id,
                        name=name,
                        category=dlg.category_input.text().strip() or None,
                        description=dlg.description_input.text().strip() or None
                    )
                    QMessageBox.information(dlg, "Saved", f"Standard expense '{name}' updated")
                    dlg.accept()
                except Exception as exc:
                    QMessageBox.warning(dlg, "Error", str(exc))
            
            dlg.save_btn.clicked.disconnect()
            dlg.save_btn.clicked.connect(update_expense)
            dlg.save_btn.setText("Update")
            
            if dlg.exec() == QDialog.Accepted:
                self.load_standard_expenses()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to edit: {str(e)}")

    def delete_standard_expense(self):
        """Delete the selected standard expense account"""
        try:
            selected_row = self.standard_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "No Selection", "Please select a standard expense account first")
                return
            
            standard_expenses = self.controller.list_standard_expenses()
            if selected_row >= len(standard_expenses):
                return
            
            standard = standard_expenses[selected_row]
            reply = QMessageBox.question(self, "Delete Standard Expense",
                                        f"Delete standard expense account '{standard.name}'?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.controller.delete_standard_expense(standard.id)
                QMessageBox.information(self, "Deleted", "Standard expense account deleted")
                self.load_standard_expenses()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to delete: {str(e)}")

    def load_expenses(self):
        try:
            try:
                start = self.start_date.date().toPython()
                end = self.end_date.date().toPython()
            except AttributeError:
                start = self.start_date.date().toPyDate()
                end = self.end_date.date().toPyDate()
            rows = self.controller.list_expenses(start, end)
            self.table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self.table.setItem(i, 0, QTableWidgetItem(r.title))  # Use title field
                self.table.setItem(i, 1, QTableWidgetItem(f"Rs {r.amount:,.2f}"))
                self.table.setItem(i, 2, QTableWidgetItem(r.category or ""))
                self.table.setItem(i, 3, QTableWidgetItem(str(r.expense_date)))
        except Exception as e:
            print(f"Error loading expenses: {e}")
            # Rollback transaction on error
            try:
                self.controller.session.rollback()
            except Exception as e:
                pass
            self.table.setRowCount(0)

    def load_recurring_expenses(self):
        try:
            # Get recurring expenses from controller
            recurring_expenses = self.controller.list_recurring_expenses()
            self.recurring_table.setRowCount(len(recurring_expenses))

            for i, rec in enumerate(recurring_expenses):
                # ExpenseSchedule doesn't have title field, use notes or generate placeholder
                notes = rec.notes or ""
                title = notes if notes else f"Recurring Expense {rec.id}"
                self.recurring_table.setItem(i, 0, QTableWidgetItem(title))
                self.recurring_table.setItem(i, 1, QTableWidgetItem(f"Rs {rec.amount:,.2f}"))
                # Parse frequency from notes field
                frequency = parse_frequency_from_notes(notes)
                self.recurring_table.setItem(i, 2, QTableWidgetItem(frequency))
                self.recurring_table.setItem(i, 3, QTableWidgetItem(str(rec.next_due_date) if rec.next_due_date else "N/A"))
                self.recurring_table.setItem(i, 4, QTableWidgetItem("Yes" if getattr(rec, 'auto_create', True) else "No"))

                # Add action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(2, 2, 2, 2)

                edit_btn = QPushButton("Edit")
                edit_btn.clicked.connect(lambda checked, idx=i: self.edit_recurring_expense(idx))
                delete_btn = QPushButton("Delete")
                delete_btn.clicked.connect(lambda checked, idx=i: self.delete_recurring_expense(idx))

                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                self.recurring_table.setCellWidget(i, 5, actions_widget)
        except Exception as e:
            print(f"Error loading recurring expenses: {e}")
            try:
                self.controller.session.rollback()
            except Exception as e:
                pass
            self.recurring_table.setRowCount(0)

    def open_create_expense(self):
        dlg = CreateExpenseDialog(self.controller, self)
        if dlg.exec() == QDialog.Accepted:
            self.load_expenses()

    def open_create_recurring(self):
        dlg = CreateRecurringExpenseDialog(self.controller, self)
        if dlg.exec() == QDialog.Accepted:
            self.load_recurring_expenses()

    def process_recurring_expenses(self):
        try:
            count = self.controller.process_recurring_expenses()
            QMessageBox.information(self, "Processed", f"Created {count} recurring expenses")
            self.load_expenses()  # Refresh regular expenses to show new ones
            self.load_recurring_expenses()  # Refresh recurring list
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to process recurring expenses: {str(e)}")

    def edit_recurring_expense(self, index):
        # Get the recurring expense from the table
        title_item = self.recurring_table.item(index, 0)
        if title_item:
            title = title_item.text()
            try:
                # Find the recurring expense by ID or notes
                recurring_expenses = self.controller.list_recurring_expenses()
                recurring = None
                for rec in recurring_expenses:
                    if (rec.notes and rec.notes in title) or (str(rec.id) in title):
                        recurring = rec
                        break

                if recurring:
                    dlg = EditRecurringExpenseDialog(self.controller, recurring, self)
                    if dlg.exec() == QDialog.Accepted:
                        self.load_recurring_expenses()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to edit recurring expense: {str(e)}")

    def delete_recurring_expense(self, index):
        title_item = self.recurring_table.item(index, 0)
        if title_item:
            title = title_item.text()
            reply = QMessageBox.question(self, "Delete Recurring Expense",
                                        f"Delete recurring expense '{title}'?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    # Find the recurring expense by ID or notes
                    recurring_expenses = self.controller.list_recurring_expenses()
                    recurring = None
                    for rec in recurring_expenses:
                        if (rec.notes and rec.notes in title) or (str(rec.id) in title):
                            recurring = rec
                            break

                    if recurring:
                        self.controller.delete_recurring_expense(str(recurring.id))  # Use ID
                        QMessageBox.information(self, "Deleted", "Recurring expense deleted")
                        self.load_recurring_expenses()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to delete: {str(e)}")

    def export_csv(self):
        try:
            start = self.start_date.date().toPython()
            end = self.end_date.date().toPython()
        except AttributeError:
            start = self.start_date.date().toPyDate()
            end = self.end_date.date().toPyDate()
        path = self.controller.export_expenses_csv(start, end)
        QMessageBox.information(self, "Exported", f"Expenses exported to: {path}")
