import os
import html

try:
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QDateEdit,
        QFrame, QMessageBox, QGroupBox, QFormLayout, QHeaderView, QAbstractItemView
    )
    from PySide6.QtPrintSupport import QPrinter, QPrintDialog
    from PySide6.QtGui import QFont, QColor, QPageSize, QPageLayout, QTextDocument
    from PySide6.QtCore import Qt, QDate, QRect, QSizeF, QMarginsF
    qt_version = "PySide6"
except ImportError:
    try:
        from PyQt6.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
            QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QDateEdit,
            QFrame, QMessageBox, QGroupBox, QFormLayout, QHeaderView, QAbstractItemView
        )
        from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
        from PyQt6.QtGui import QFont, QColor, QPageSize, QPageLayout, QTextDocument
        from PyQt6.QtCore import Qt, QDate, QRect, QSizeF, QMarginsF
        qt_version = "PyQt6"
    except ImportError:
        raise ImportError("Neither PySide6 nor PyQt6 is available. Please install one of them.")
from pos_app.models.database import Customer, Sale, Payment, SaleItem
from datetime import datetime, time
import json

class CustomerStatementDialog(QDialog):
    def __init__(self, controllers, customer_id, parent=None):
        super().__init__(parent)
        self.controllers = controllers
        self.customer_id = customer_id
        self.output_dir = os.path.join(os.getcwd(), "documents")
        os.makedirs(self.output_dir, exist_ok=True)
        self.setup_ui()
        self.load_customer_data()
        self.load_statement_data()

    def setup_ui(self):
        self.setWindowTitle("Customer Statement")
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header with customer info
        header_layout = QHBoxLayout()

        self.customer_info_label = QLabel("Customer: Loading...")
        self.customer_info_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1e293b;
            padding: 10px;
            background: #f8fafc;
            border-radius: 8px;
            border: 2px solid #e2e8f0;
        """)
        header_layout.addWidget(self.customer_info_label)

        # Export buttons
        export_btn = QPushButton("Export PDF")
        export_btn.setProperty('accent', 'Qt.blue')
        export_btn.setMinimumHeight(40)
        export_btn.clicked.connect(self.export_pdf)

        print_btn = QPushButton("Print")
        print_btn.setProperty('accent', 'Qt.green')
        print_btn.setMinimumHeight(40)
        print_btn.clicked.connect(self.print_statement)

        header_layout.addStretch()
        header_layout.addWidget(export_btn)
        header_layout.addWidget(print_btn)

        layout.addLayout(header_layout)

        # Filters
        filters_group = QGroupBox("Filters")
        filters_layout = QHBoxLayout(filters_group)

        filters_layout.addWidget(QLabel("From:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-3))
        self.start_date.setCalendarPopup(True)
        filters_layout.addWidget(self.start_date)

        filters_layout.addWidget(QLabel("To:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        filters_layout.addWidget(self.end_date)

        self.transaction_type = QComboBox()
        self.transaction_type.addItems(["All", "Sales", "Payments", "Discounts"])
        filters_layout.addWidget(QLabel("Type:"))
        filters_layout.addWidget(self.transaction_type)

        filter_btn = QPushButton("🔍 Filter")
        filter_btn.clicked.connect(self.load_statement_data)
        filters_layout.addWidget(filter_btn)

        layout.addWidget(filters_group)

        # Summary cards
        summary_layout = QHBoxLayout()

        self.total_sales_label = QLabel("Total Sales: Rs 0.00")
        self.total_payments_label = QLabel("Total Payments: Rs 0.00")
        self.total_discounts_label = QLabel("Total Discounts: Rs 0.00")
        self.outstanding_label = QLabel("Amount Due: Rs 0.00")

        for label in [self.total_sales_label, self.total_payments_label, self.total_discounts_label, self.outstanding_label]:
            label.setStyleSheet("""
                padding: 15px;
                background: #f1f5f9;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                color: #334155;
                text-align: center;
            """)
            summary_layout.addWidget(label)

        layout.addLayout(summary_layout)

        # Statement table
        table_group = QGroupBox("Transaction History")
        table_layout = QVBoxLayout(table_group)

        self.table = QTableWidget()
        self.table.setColumnCount(5)  # Fixed: Only 5 columns needed
        self.table.setHorizontalHeaderLabels([
            "Date", "Description", "Debit", "Credit", "Balance"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Date
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Description
        header.resizeSection(0, 120)
        header.resizeSection(1, 200)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)

        table_layout.addWidget(self.table)
        layout.addWidget(table_group)

        # Action buttons
        buttons_layout = QHBoxLayout()

        close_btn = QPushButton("❌ Close")
        close_btn.setProperty('accent', 'Qt.red')
        close_btn.clicked.connect(self.reject)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setProperty('accent', 'Qt.blue')
        refresh_btn.clicked.connect(self.load_statement_data)

        buttons_layout.addWidget(refresh_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

    def load_customer_data(self):
        """Load customer information"""
        try:
            customer = self.controllers['customers'].session.get(Customer, self.customer_id)
            if customer:
                self.customer_info_label.setText(f"Customer: {customer.name} (ID: {customer.id})")
            else:
                self.customer_info_label.setText("Customer not found")
        except Exception as e:
            self.customer_info_label.setText(f"Error loading customer: {str(e)}")

    def load_statement_data(self):
        """Load customer statement data"""
        try:
            print("DEBUG: Starting to load statement data...")
            
            # Convert QDate to Python date (compatible with both PyQt6 and PySide6)
            try:
                start_date = self.start_date.date().toPython()
            except AttributeError:
                # PyQt6 doesn't have toPython(), use toString() and parse
                start_date_str = self.start_date.date().toString("yyyy-MM-dd")
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            
            try:
                end_date = self.end_date.date().toPython()
            except AttributeError:
                # PyQt6 doesn't have toPython(), use toString() and parse
                end_date_str = self.end_date.date().toString("yyyy-MM-dd")
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            # Convert to datetime with time boundaries
            start_dt = datetime.combine(start_date, time.min)  # Start of day
            end_dt = datetime.combine(end_date, time.max)      # End of day (23:59:59.999999)
            
            trans_type = self.transaction_type.currentText()
            
            # Get customer data first
            customer = self.controllers['customers'].session.get(Customer, self.customer_id)
            if not customer:
                print(f"ERROR: Customer {self.customer_id} not found!")
                QMessageBox.warning(self, "Error", "Customer not found!")
                return
            
            print(f"DEBUG: Found customer: {customer.name}")
            self.customer = customer  # Store for printing

            # Get sales for this customer (with item names)
            sales = []
            if trans_type in ["All", "Sales"]:
                try:
                    # Use direct session query for better control
                    from sqlalchemy.orm import joinedload
                    from sqlalchemy import case

                    latest_sale = self.controllers['customers'].session.query(Sale).options(
                        joinedload(Sale.items).joinedload(SaleItem.product)
                    ).filter(
                        Sale.customer_id == self.customer_id,
                        Sale.sale_date >= start_dt,
                        Sale.sale_date <= end_dt
                    ).order_by(
                        case((Sale.sale_date == None, 1), else_=0),
                        Sale.sale_date.desc(),
                        Sale.id.desc()
                    ).first()
                    
                    sales = [latest_sale] if latest_sale else []
                    
                    print(f"DEBUG: Found {len(sales)} sales for customer {self.customer_id}")
                    
                except Exception as e:
                    print(f"ERROR loading sales: {e}")
                    import traceback
                    traceback.print_exc()
                    try:
                        self.controllers['customers'].session.rollback()
                    except Exception:
                        pass
                    sales = []

            # Get payments for this customer
            payments = []
            if trans_type in ["All", "Payments"]:
                try:
                    # Use direct session query for better control
                    payments = self.controllers['customers'].session.query(Payment).filter(
                        Payment.customer_id == self.customer_id,
                        Payment.payment_date >= start_dt,
                        Payment.payment_date <= end_dt
                    ).order_by(Payment.payment_date.asc()).all()  # Oldest first for proper statement view
                    
                    print(f"DEBUG: Found {len(payments)} payments for customer {self.customer_id}")
                    
                    # Debug: Print first payment details
                    if payments:
                        first_payment = payments[0]
                        print(f"DEBUG: First payment - ID: {first_payment.id}, Date: {first_payment.payment_date}, Amount: {first_payment.amount}")
                        
                except Exception as e:
                    print(f"ERROR loading payments: {e}")
                    import traceback
                    traceback.print_exc()
                    try:
                        self.controllers['customers'].session.rollback()
                    except Exception:
                        pass
                    payments = []

            # Combine and sort transactions
            transactions = []

            # Add products from sales - show ONLY the latest order
            print(f"DEBUG: Sales processing - Total sales found: {len(sales)}")
            if sales:  # Only process if there are sales
                print(f"DEBUG: Processing only the latest sale")
                
                for sale_idx, sale in enumerate(sales):
                    print(f"DEBUG: Processing sale {sale_idx+1}: ID {sale.id}, Date {sale.sale_date}, Invoice {getattr(sale, 'invoice_number', 'N/A')}")
                    
                    try:
                        items = list(getattr(sale, 'items', []) or [])
                        print(f"DEBUG: Found {len(items)} items in sale")
                        
                        if items:
                            # Add each product from the sale as a separate row
                            for idx, it in enumerate(items):
                                try:
                                    product = getattr(it, 'product', None)
                                    product_name = getattr(product, 'name', 'Unknown Product') if product else 'Unknown Product'
                                    quantity = getattr(it, 'quantity', 1) or 1
                                    unit_price = getattr(it, 'unit_price', getattr(it, 'price', 0)) or 0
                                    
                                    # Use sale's total_amount instead of item subtotal to include discounts
                                    # For multi-item sales, calculate proportionate amount
                                    sale_total = getattr(sale, 'total_amount', 0) or 0
                                    sale_subtotal = getattr(sale, 'subtotal', 0) or 0
                                    
                                    if sale_subtotal > 0:
                                        # Calculate proportionate amount based on discount
                                        # Use item.total instead of item.subtotal since subtotal might be 0
                                        item_total = getattr(it, 'total', getattr(it, 'subtotal', unit_price * quantity)) or (unit_price * quantity)
                                        proportion = item_total / sale_subtotal
                                        final_amount = sale_total * proportion
                                        print(f"DEBUG: Item total: {item_total}, Sale subtotal: {sale_subtotal}, Proportion: {proportion:.4f}, Final amount: {final_amount}")
                                    else:
                                        # Fallback to item total if no sale subtotal
                                        final_amount = getattr(it, 'total', getattr(it, 'subtotal', unit_price * quantity)) or (unit_price * quantity)
                                    
                                    invoice_num = getattr(sale, 'invoice_number', f"INV-{sale.id}")
                                    
                                    print(f"DEBUG: Processing item {idx+1}: {product_name}, Qty: {quantity}, Price: {unit_price}, Item Subtotal: {getattr(it, 'subtotal', 'N/A')}, Final Amount: {final_amount}")
                                    
                                    transactions.append({
                                        'date': sale.sale_date,
                                        'type': 'Sale',
                                        'description': f"{product_name} ({invoice_num})",
                                        'debit': final_amount,
                                        'credit': 0,
                                        'reference': sale.id
                                    })
                                except Exception as e:
                                    print(f"DEBUG: ✗ Error processing item {idx+1}: {e}")
                                    import traceback
                                    traceback.print_exc()
                                    continue
                            
                            # Add discount as a separate line item if discount was applied
                            discount_amount = getattr(sale, 'discount_amount', 0) or 0
                            if discount_amount > 0:
                                invoice_num = getattr(sale, 'invoice_number', f"INV-{sale.id}")
                                print(f"DEBUG: Adding discount line: {invoice_num} - Rs {discount_amount}")
                                
                                transactions.append({
                                    'date': sale.sale_date,
                                    'type': 'Discount',
                                    'description': f"Discount Given ({invoice_num})",
                                    'debit': 0,
                                    'credit': discount_amount,  # Credit reduces the balance
                                    'reference': f"discount_{sale.id}"
                                })
                        else:
                            print(f"DEBUG: No items found in sale")
                            # No items in the sale, show as single line
                            sale_amount = getattr(sale, 'total_amount', 0) or 0
                            invoice_num = getattr(sale, 'invoice_number', f"INV-{sale.id}")
                            
                            transactions.append({
                                'date': sale.sale_date,
                                'type': 'Sale',
                                'description': f"Sale Items ({invoice_num})",
                                'debit': sale_amount,
                                'credit': 0,
                                'reference': sale.id
                            })
                            print(f"DEBUG: Added sale summary: {invoice_num} - Rs {sale_amount}")
                            
                            # Add discount as a separate line item if discount was applied
                            discount_amount = getattr(sale, 'discount_amount', 0) or 0
                            if discount_amount > 0:
                                print(f"DEBUG: Adding discount line: {invoice_num} - Rs {discount_amount}")
                                
                                transactions.append({
                                    'date': sale.sale_date,
                                    'type': 'Discount',
                                    'description': f"Discount Given ({invoice_num})",
                                    'debit': 0,
                                    'credit': discount_amount,  # Credit reduces the balance
                                    'reference': f"discount_{sale.id}"
                                })
                            
                    except Exception as e:
                        print(f"DEBUG: ✗ Error processing sale: {e}")
                        import traceback
                        traceback.print_exc()
                        # Fallback: show sale as single line
                        sale_amount = getattr(sale, 'total_amount', 0) or 0
                        invoice_num = getattr(sale, 'invoice_number', f"INV-{sale.id}")
                        
                        transactions.append({
                            'date': sale.sale_date,
                            'type': 'Sale',
                            'description': f"Sale Items ({invoice_num})",
                            'debit': sale_amount,
                            'credit': 0,
                            'reference': sale.id
                        })
                        print(f"DEBUG: Added fallback sale: {invoice_num} - Rs {sale_amount}")
                        
                        # Add discount as a separate line item if discount was applied
                        discount_amount = getattr(sale, 'discount_amount', 0) or 0
                        if discount_amount > 0:
                            print(f"DEBUG: Adding fallback discount line: {invoice_num} - Rs {discount_amount}")
                            
                            transactions.append({
                                'date': sale.sale_date,
                                'type': 'Discount',
                                'description': f"Discount Given ({invoice_num})",
                                'debit': 0,
                                'credit': discount_amount,  # Credit reduces the balance
                                'reference': f"discount_{sale.id}"
                            })
                
            else:
                print(f"DEBUG: ✗ No sales found to process!")

            # Add payments as credit transactions
            for payment in payments:
                try:
                    pm = getattr(payment, 'payment_method', None)
                    pm_text = str(pm) if pm is not None else 'N/A'
                except Exception:
                    pm_text = 'N/A'
                
                payment_amount = getattr(payment, 'amount', 0) or 0
                
                transactions.append({
                    'date': payment.payment_date,
                    'type': 'Payment',
                    'description': f"Payment - {pm_text}",
                    'debit': 0,
                    'credit': payment_amount,
                    'reference': payment.id
                })
                print(f"DEBUG: Added payment transaction: {payment.payment_date} - {pm_text} - Rs {payment_amount}")

            # Sort by date (most recent first)
            transactions.sort(key=lambda x: x['date'], reverse=True)

            # Calculate running balance
            balance = 0.0
            for trans in transactions:
                balance += trans['credit'] - trans['debit']
                trans['balance'] = balance

            print(f"DEBUG: Total transactions to display: {len(transactions)}")
            
            # Filter transactions based on selected type
            if trans_type != "All":
                print(f"DEBUG: Filtering by transaction type: {trans_type}")
                filtered_transactions = []
                for trans in transactions:
                    if trans_type == "Sales" and trans['type'] in ['Sale', 'Discount']:
                        # Include both Sales and Discount lines when "Sales" is selected
                        filtered_transactions.append(trans)
                    elif trans_type == "Payments" and trans['type'] == 'Payment':
                        filtered_transactions.append(trans)
                    elif trans_type == "Discounts" and trans['type'] == 'Discount':
                        filtered_transactions.append(trans)
                transactions = filtered_transactions
                print(f"DEBUG: After filtering: {len(transactions)} transactions")
            
            # Debug: Print all transactions that will be displayed
            for i, trans in enumerate(transactions):
                print(f"DEBUG: Transaction {i+1}: {trans['date']} - {trans['type']} - {trans['description']} - Debit: {trans['debit']}, Credit: {trans['credit']}")

            # Update table
            self.table.setRowCount(len(transactions))

            if not transactions:
                print("DEBUG: No transactions found - showing empty message")
                # Show a message when no transactions found
                self.table.setRowCount(1)
                self.table.setSpan(0, 0, 1, 5)  # Span all columns
                no_data_item = QTableWidgetItem("No transactions found for the selected period")
                no_data_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(0, 0, no_data_item)
                
                # Clear summary
                self.total_sales_label.setText("Total Sales: Rs 0.00")
                self.outstanding_label.setText("Amount Due: Rs 0.00")
                self.outstanding_label.setStyleSheet("""
                    padding: 15px;
                    background: #f1f5f9;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #000000;
                    text-align: center;
                """)
            else:
                print(f"DEBUG: Populating table with {len(transactions)} transactions")
                # Fill table with transaction data
                for row, trans in enumerate(transactions):
                    # Date
                    date_item = QTableWidgetItem(trans['date'].strftime('%Y-%m-%d'))
                    date_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, 0, date_item)
                    
                    # Description
                    desc_item = QTableWidgetItem(trans['description'])
                    self.table.setItem(row, 1, desc_item)
                    
                    # Debit - only show if > 0
                    debit_text = f"Rs {trans['debit']:.2f}" if trans['debit'] > 0 else ""
                    debit_item = QTableWidgetItem(debit_text)
                    debit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.table.setItem(row, 2, debit_item)
                    
                    # Credit - only show if > 0
                    credit_text = f"Rs {trans['credit']:.2f}" if trans['credit'] > 0 else ""
                    credit_item = QTableWidgetItem(credit_text)
                    credit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.table.setItem(row, 3, credit_item)
                    
                    # Balance - always show
                    balance_item = QTableWidgetItem(f"Rs {trans['balance']:.2f}")
                    balance_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    if trans['balance'] < 0:
                        balance_item.setBackground(QColor('#fee2e2'))  # Light red for negative
                    self.table.setItem(row, 4, balance_item)

                total_sales = sum(t['debit'] for t in transactions if t.get('type') == 'Sale')
                total_discounts = sum(t['credit'] for t in transactions if t.get('type') == 'Discount')
                total_payments = sum(t['credit'] for t in transactions if t.get('type') == 'Payment')
                # Amount Due comes from database (Customer.current_credit)
                amount_due = float(getattr(customer, 'current_credit', 0) or 0)

                self.total_sales_label.setText(f"Total Sales: Rs {total_sales:.2f}")
                self.total_payments_label.setText(f"Total Payments: Rs {total_payments:.2f}")
                self.total_discounts_label.setText(f"Total Discounts: Rs {total_discounts:.2f}")
                self.outstanding_label.setText(f"Amount Due: Rs {amount_due:.2f}")

                # Amount Due is always shown in red (debt color)
                color = '#dc2626' if amount_due > 0 else '#000000'
                self.outstanding_label.setStyleSheet(
                    f"padding: 15px; background: #f1f5f9; border-radius: 8px; font-size: 14px; font-weight: bold; color: {color}; text-align: center;"
                )
                
        except Exception as e:
            print(f"CRITICAL ERROR in load_statement_data: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to load statement data: {str(e)}")

    def export_pdf(self):
        """Export statement to PDF using HTML rendering"""
        filename = f"customer_statement_{self.customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(filepath)
        printer.setPageSize(QPageSize(QPageSize.Legal))
        printer.setPageOrientation(QPageLayout.Orientation.Portrait)
        printer.setPageMargins(QMarginsF(12.7, 12.7, 12.7, 18), QPageLayout.Unit.Millimeter)

        html_content = self._build_statement_html()
        self._print_html_document(printer, html_content)

        QMessageBox.information(self, "Exported", f"Statement exported to: {filepath}")

    def _build_statement_html(self):
        print("[DEBUG] _build_statement_html method called")
        try:
            start_date, end_date = self._get_selected_dates()
            data = self._gather_statement_data(start_date, end_date)
            print(f"[DEBUG] _build_statement_html - gathered data keys: {list(data.keys())}")
            print(f"[DEBUG] _build_statement_html - total_sales: {data.get('total_sales', 'N/A')}")
            print(f"[DEBUG] _build_statement_html - total_discounts: {data.get('total_discounts', 'N/A')}")
            
            shop_info = self._get_shop_info()
            customer_name = getattr(self.customer, "name", "N/A") if getattr(self, "customer", None) else "N/A"
            customer_address = getattr(self.customer, "address", "N/A") if getattr(self, "customer", None) else "N/A"
            customer_phone = getattr(self.customer, "phone", "N/A") if getattr(self, "customer", None) else "N/A"
            period_text = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            generated_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"[ERROR] _build_statement_html error: {e}")
            raise

        def esc(value):
            return html.escape(str(value) if value is not None else "")

        rows_html = []
        combined_rows = data["sale_rows"] + data["payment_rows"]
        if not combined_rows:
            rows_html.append(
                "<tr><td colspan='7' class='empty'>No transactions found for the selected period.</td></tr>"
            )
        else:
            for row in combined_rows:
                rows_html.append(
                    "<tr>"
                    f"<td>{esc(row['date'])}</td>"
                    f"<td>{esc(row['invoice'])}</td>"
                    f"<td>{esc(row['description'])}</td>"
                    f"<td class='numeric'>{esc(row['quantity'])}</td>"
                    f"<td class='numeric'>{esc(row['discount'])}</td>"
                    f"<td class='numeric'>{esc(row['price'])}</td>"
                    f"<td class='numeric'>{esc(row['subtotal'])}</td>"
                    "</tr>"
                )

        summary_cards = [
            ("Total Sales", self._format_currency(data["total_sales"])),
        ]
        
        # Debug: Check if discount data is available
        total_sales = data.get('total_sales', 0)
        total_discounts = data.get('total_discounts', 0)
        
        print(f"[DEBUG] HTML generation - total_sales: {total_sales} (type: {type(total_sales)})")
        print(f"[DEBUG] HTML generation - total_discounts: {total_discounts} (type: {type(total_discounts)})")
        
        # Ensure discount is a number
        try:
            total_discounts = float(total_discounts) if total_discounts else 0.0
        except (ValueError, TypeError):
            total_discounts = 0.0
        
        print(f"[DEBUG] HTML generation - total_discounts after conversion: {total_discounts}")
        
        # Add discount line if there's a discount
        if total_discounts > 0:
            discount_card = ("Discount Given", self._format_currency(-total_discounts))
            summary_cards.append(discount_card)
            print(f"[DEBUG] Added discount card: {discount_card}")
        else:
            print(f"[DEBUG] No discount to add (total_discounts <= 0): {total_discounts}")
        
        summary_cards.append(("Amount Due", self._format_currency(data["balance"])))
        
        print(f"[DEBUG] Final summary cards: {summary_cards}")
        
        summary_html = "".join(
            f"<div class='summary-card{' discount-card' if 'Discount' in label else ''}'><div class='label'>{esc(label)}</div>"
            f"<div class='value{' discount-value' if 'Discount' in label else ''}'>{esc(value)}</div></div>"
            for label, value in summary_cards
        )

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <style>
        @page {{
            margin: 18mm;
        }}
        body {{
            font-family: 'Segoe UI', 'Arial', sans-serif;
            margin: 0;
            padding: 0.5in;
            color: #0f172a;
            background: #ffffff;
            font-size: 16pt;
            line-height: 1.4;
        }}
        .header {{
            text-align: center;
            margin-bottom: 0.8rem;
        }}
        .header h1 {{
            margin: 0;
            font-size: 1.8em;
            letter-spacing: 0.12em;
        }}
        .header p {{
            margin: 0.2rem 0;
            color: #475569;
            font-size: 1.1em;
        }}
        .bill-to {{
            margin-top: 1rem;
            padding: 0.8rem;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            background: #f8fafc;
        }}
        .bill-to h2 {{
            margin: 0 0 0.5rem 0;
            font-size: 1.1em;
            color: #475569;
            letter-spacing: 0.08em;
        }}
        .summary-section {{
            margin-top: 1rem;
        }}
        .summary-card {{
            display: inline-block;
            min-width: 120px;
            margin-right: 1rem;
            margin-bottom: 0.5rem;
            padding: 0.7rem 0.8rem;
            border-radius: 4px;
            background: linear-gradient(135deg, #eef2ff, #eff6ff);
            border: 1px solid #dbeafe;
        }}
        .summary-card .label {{
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 0.12em;
            color: #6366f1;
            margin-bottom: 0.3rem;
        }}
        .summary-card .value {{
            font-size: 1.2em;
            font-weight: 700;
        }}
        .discount-card {{
            background: linear-gradient(135deg, #fef2f2, #fee2e2) !important;
            border: 2px solid #ef4444 !important;
        }}
        .discount-card .label {{
            color: #dc2626 !important;
        }}
        .discount-card .value {{
            color: #dc2626 !important;
            font-weight: 800 !important;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20pt auto 15pt auto;
            table-layout: fixed;
            font-size: 14pt;
            border: 1pt solid #1e293b;
            border-radius: 4pt;
            overflow: hidden;
        }}
        th {{
            padding: 10pt 8pt;
            background: #1e293b !important;
            color: #ffffff !important;
            font-size: 14pt !important;
            font-weight: bold !important;
            border: 1px solid #ffffff !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            line-height: 1.2;
        }}
        td {{
            padding: 1.2rem 1.8rem;
            border: 2px solid #e2e8f0;
            font-size: 12pt;
            color: #0f172a;
            vertical-align: middle;
            text-align: center;
            background: #ffffff;
            font-weight: 500;
        }}
        td.numeric {{
            text-align: right;
            font-variant-numeric: tabular-nums;
        }}
        tr:nth-child(even) td {{
            background-color: #f8fafc;
        }}
        tr {{
            min-height: 2rem;
        }}
        .section-title {{
            margin-top: 20pt;
            font-size: 12pt;
            letter-spacing: 0.22em;
            color: #94a3b8;
        }}
        .footer {{
            margin-top: 30pt;
            text-align: center;
            font-size: 12pt;
            color: #94a3b8;
        }}
        .empty {{
            text-align: center;
            padding: 20pt 0;
            color: #94a3b8;
            font-size: 14pt;
        }}
        .total-row {{
            background-color: #f1f5f9;
            font-weight: bold;
        }}
        .due-row {{
            background-color: #fef2f2;
            color: #dc2626;
            font-weight: bold;
        }}
        .footer-cell-label {{
            text-align: right;
            padding: 8pt 10pt;
            font-size: 14pt;
        }}
        .footer-cell-value {{
            text-align: center;
            padding: 8pt 10pt;
            font-size: 16pt;
        }}
    </style>
</head>
<body>
    <div class="header">
        <p class="section-title">CUSTOMER STATEMENT</p>
        <h1>{esc(shop_info['name'])}</h1>
        <p>{esc(shop_info['address'])}</p>
        <p>Contact: {esc(shop_info['phone'])}</p>
        <p>Statement Period: {esc(period_text)}</p>
    </div>

    <div class="bill-to">
        <h2>BILL TO</h2>
        <p><strong>Name:</strong> {esc(customer_name)}</p>
        <p><strong>Address:</strong> {esc(customer_address)}</p>
        <p><strong>Phone:</strong> {esc(customer_phone)}</p>
    </div>

    <table>
        <thead>
            <tr>
                <th>DATE</th>
                <th>INVOICE #</th>
                <th>DESCRIPTION</th>
                <th>QTY</th>
                <th>DISCOUNT</th>
                <th>PRICE</th>
                <th>SUBTOTAL</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows_html)}
        </tbody>
        <tfoot>
            <tr class="total-row">
                <td colspan="6" class="footer-cell-label">TOTAL OF THAT SALE:</td>
                <td class="footer-cell-value">{self._format_currency(data["total_sales"])}</td>
            </tr>
            {f'''<tr class="due-row">
                <td colspan="6" class="footer-cell-label">DISCOUNT GIVEN:</td>
                <td class="footer-cell-value">{self._format_currency(-data["total_discounts"])}</td>
            </tr>''' if data.get("total_discounts", 0) > 0 else ""}
            <tr class="due-row">
                <td colspan="6" class="footer-cell-label">AMOUNT DUE:</td>
                <td class="footer-cell-value">{self._format_currency(data["balance"])}</td>
            </tr>
        </tfoot>
    </table>

    <div class="footer">
        <p>Generated on {esc(generated_text)}</p>
        <p>Thank you for your business!</p>
    </div>
</body>
</html>
"""
        return html_content

    def _gather_statement_data(self, start_date, end_date):
        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(end_date, time.max)
        session = self.controllers['customers'].session
        
        # Get customer's current balance from database
        customer = session.get(Customer, self.customer_id)
        current_credit = float(getattr(customer, 'current_credit', 0) or 0)
        
        # Get the latest completed sale within the date range (deterministic ordering)
        from sqlalchemy.orm import joinedload
        from sqlalchemy import case

        latest_sale = session.query(Sale).options(
            joinedload(Sale.items).joinedload(SaleItem.product)
        ).filter(
            Sale.customer_id == self.customer_id,
            Sale.sale_date >= start_dt,
            Sale.sale_date <= end_dt
        ).order_by(
            case((Sale.sale_date == None, 1), else_=0),
            Sale.sale_date.desc(),
            Sale.id.desc()
        ).first()
        
        sales = [latest_sale] if latest_sale else []

        sale_rows = []
        if sales:
            # Process only the latest sale
            for sale_idx, sale in enumerate(sales):
                sale_date_text = sale.sale_date.strftime('%Y-%m-%d') if sale.sale_date else ""
                invoice_no = getattr(sale, 'invoice_number', '') or ''
                items = list(getattr(sale, 'items', []) or [])
                
                if not items:
                    # No items in sale, show as single line
                    subtotal = getattr(sale, 'total_amount', 0) or 0
                    sale_rows.append({
                        "date": sale_date_text,
                        "invoice": invoice_no,
                        "description": "Sale Items",
                        "quantity": str(getattr(sale, 'total_quantity', 1) or 1),
                        "discount": "-",
                        "price": self._format_currency(subtotal),
                        "subtotal": self._format_currency(subtotal)
                    })
                else:
                    # Add each product from the sale as a separate row
                    # Calculate proportional amounts based on discount
                    sale_total = getattr(sale, 'total_amount', 0) or 0
                    sale_subtotal = getattr(sale, 'subtotal', 0) or 0
                    
                    for idx, item in enumerate(items):
                        product = getattr(item, 'product', None)
                        product_name = getattr(product, 'name', 'Unknown Item') if product else 'Unknown Item'
                        quantity = getattr(item, 'quantity', 1) or 1
                        discount = getattr(item, 'discount', 0)
                        unit_price = getattr(item, 'unit_price', getattr(item, 'price', 0)) or 0
                        
                        # Calculate proportionate amount based on discount
                        if sale_subtotal > 0:
                            item_total = getattr(item, 'total', getattr(item, 'subtotal', unit_price * quantity)) or (unit_price * quantity)
                            proportion = item_total / sale_subtotal
                            final_amount = sale_total * proportion
                            print(f"[DEBUG] Printed item: {product_name}, Item total: {item_total}, Proportion: {proportion:.4f}, Final amount: {final_amount}")
                        else:
                            # Fallback to item total if no sale subtotal
                            final_amount = getattr(item, 'total', getattr(item, 'subtotal', unit_price * quantity)) or (unit_price * quantity)
                        
                        if isinstance(discount, (int, float)):
                            discount_text = f"{discount:.1f}%"
                        else:
                            discount_text = str(discount or "-")
                        
                        sale_rows.append({
                            "date": sale_date_text if idx == 0 else "",
                            "invoice": invoice_no if idx == 0 else "",
                            "description": product_name,
                            "quantity": str(quantity),
                            "discount": discount_text,
                            "price": self._format_currency(unit_price),
                            "subtotal": self._format_currency(final_amount)  # Use the discounted amount
                        })

        # Calculate total_sales for the latest sale only - use total_amount (after discount)
        total_sales = 0.0
        total_discounts = 0.0
        if sales:
            latest_sale = sales[0]
            # Use the sale's total_amount which already includes discounts
            total_sales = getattr(latest_sale, 'total_amount', 0) or 0
            total_discounts = getattr(latest_sale, 'discount_amount', 0) or 0
            print(f"[DEBUG] Printed statement - using total_amount: Rs {total_sales} from sale {getattr(latest_sale, 'invoice_number', latest_sale.id)}")
            print(f"[DEBUG] Printed statement - discount amount: Rs {total_discounts}")
        
        # Get all payments made by this customer in the date range
        # Get payments within the date range
        payments = session.query(Payment).filter(
            Payment.customer_id == self.customer_id,
            Payment.payment_date >= start_dt,
            Payment.payment_date <= end_dt,
            Payment.payment_method != 'CREDIT'  # Exclude credit bookkeeping entries
        ).all()
        
        total_payments = sum(getattr(payment, 'amount', 0) or 0 for payment in payments)

        # Amount Due comes from database (Customer.current_credit)
        amount_due = current_credit
        
        return {
            "sale_rows": sale_rows,
            "payment_rows": [],  # Empty payment rows
            "opening_balance": 0,  # Not needed
            "total_sales": total_sales,
            "total_discounts": total_discounts,  # Add discount amount
            "total_payments": 0,  # Not used anymore
            "balance": amount_due  # Amount Due = Customer.current_credit from DB
        }

    def _print_html_document(self, printer, html_content):
        document = QTextDocument()
        document.setDocumentMargin(24)  # Increased margin for Legal alignment
        document.setDefaultFont(QFont("Segoe UI", 12))  # Increased font size for readability
        document.setHtml(html_content)

        try:
            # For ScreenResolution, we use logical dots
            page_layout = printer.pageLayout()
            paint_rect = page_layout.paintRectPixels(printer.resolution())
            print(f"DEBUG: Page dimensions (Pixels at {printer.resolution()} DPI): {paint_rect.width()}x{paint_rect.height()}")
            document.setPageSize(QSizeF(paint_rect.width(), paint_rect.height()))
        except Exception as e:
            print(f"ERROR setting page size: {e}")
            # Fallback
            document.setPageSize(QSizeF(printer.width(), printer.height()))

        if hasattr(document, "print"):
            document.print(printer)
        else:
            document.print_(printer)

    def _get_selected_dates(self):
        def to_py_date(qdate):
            try:
                return qdate.toPython()
            except AttributeError:
                return datetime.strptime(qdate.toString("yyyy-MM-dd"), "%Y-%m-%d").date()

        return to_py_date(self.start_date.date()), to_py_date(self.end_date.date())

    def _format_currency(self, value):
        try:
            return f"Rs {float(value):,.2f}"
        except Exception:
            return f"Rs {value}"

    def _get_shop_info(self):
        """Get shop information from settings"""
        try:
            try:
                from PySide6.QtCore import QSettings
            except ImportError:
                from PyQt6.QtCore import QSettings

            settings = QSettings()
            shop_name = settings.value("business_name", "Sarhad General Store")
            shop_address = settings.value("business_address", "Madni Chowk")
            shop_phone = settings.value("business_phone", "+923225031977")

            return {
                'name': shop_name,
                'address': shop_address,
                'phone': shop_phone
            }
        except Exception:
            # Fallback values
            return {
                'name': "Your Shop Name",
                'address': "Your Address",
                'phone': "Your Phone"
            }

    def print_statement(self):
        """Print customer statement with proper formatting and printer selection"""
        try:
            from PySide6.QtPrintSupport import QPrinter, QPrintDialog
            from PySide6.QtGui import QPageSize, QPageLayout
        except ImportError:
            from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
            from PyQt6.QtGui import QPageSize, QPageLayout

        print("[DEBUG] Print statement method called")
        
        # Create printer - Use default (ScreenResolution) for better HTML scaling
        printer = QPrinter()
        printer.setPageSize(QPageSize(QPageSize.Legal))
        printer.setPageOrientation(QPageLayout.Orientation.Portrait)

        # Show printer selection dialog
        dialog = QPrintDialog(printer, self)
        dialog.setWindowTitle("Print Customer Statement")
        if dialog.exec() != QPrintDialog.Accepted:
            print("[DEBUG] Print dialog cancelled")
            return

        print("[DEBUG] Print dialog accepted, generating HTML...")
        html_content = self._build_statement_html()
        print(f"[DEBUG] HTML content length: {len(html_content)} characters")
        print(f"[DEBUG] HTML content preview: {html_content[:500]}...")
        
        # Save HTML to file for debugging
        try:
            import os
            from datetime import datetime
            debug_filename = f"debug_statement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            debug_path = os.path.join(os.path.dirname(__file__), "..", debug_filename)
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"[DEBUG] HTML content saved to: {debug_path}")
        except Exception as e:
            print(f"[DEBUG] Error saving HTML file: {e}")
        
        self._print_html_document(printer, html_content)
        print("[DEBUG] Print document sent to printer")

    def add_print_button(self):
        """Add a print button to the customer statement dialog"""
        try:
            # Find the button layout or create one
            button_layout = QHBoxLayout()
            
            print_btn = QPushButton("Print Statement")
            print_btn.clicked.connect(self.print_statement)
            print_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #1d4ed8;
                }
                QPushButton:pressed {
                    background-color: #1e40af;
                }
            """)
            
            button_layout.addWidget(print_btn)
            button_layout.addStretch()
            
            # Add to main layout
            self.layout().addLayout(button_layout)
            
        except Exception as e:
            print(f"Error adding print button: {e}")
