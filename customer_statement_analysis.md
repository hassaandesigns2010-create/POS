# 📄 Customer Statement Printing Logic Analysis

## 🎯 **Complete Customer Statement Flow**

### 📋 **File Structure & Components**

#### **1. Main Entry Point: `views/customers.py`**
- **Button:** `📄 Statement` button in customer management UI
- **Method:** `statement_selected()` → `_statement(customer_id)`
- **Signal:** Emits `action_export_statement.emit(customer_id)`

#### **2. Signal Routing: `views/main_window.py`**
- **Connection:** `customers.action_export_statement.connect(self._show_customer_statement)`
- **Handler:** `_show_customer_statement(customer_id)`
- **Action:** Creates and shows `CustomerStatementDialog`

#### **3. Core Logic: `views/customer_statement.py`**
- **Class:** `CustomerStatementDialog(QDialog)`
- **Main Methods:** `export_pdf()`, `print_statement()`
- **HTML Generation:** `_build_statement_html()`

---

## 🔍 **Detailed Printing Logic Analysis**

### **📊 Data Gathering Process:**

#### **1. Customer Data Loading (`load_customer_data`)**
```python
customer = self.controllers['customers'].session.get(Customer, self.customer_id)
```

#### **2. Statement Data Loading (`load_statement_data`)**
- **Date Range:** User-selected start/end dates
- **Transaction Types:** "All", "Sales", "Payments", "Discounts"
- **Latest Sale Only:** Shows ONLY the most recent sale (not all sales)
- **Payment Records:** All payments in date range

#### **3. HTML Generation (`_build_statement_html`)**
- **Template:** Professional HTML with CSS styling
- **Shop Info:** Business name, address, phone from settings
- **Customer Info:** Name, address, phone
- **Transaction Table:** Date, Invoice, Description, Qty, Discount, Price, Subtotal
- **Summary Cards:** Total Sales, Discounts, Amount Due

---

## 🖨️ **Printing Implementation**

### **PDF Export Flow:**
```python
export_pdf() → _build_statement_html() → _print_html_document() → QPrinter
```

### **Print Dialog Flow:**
```python
print_statement() → QPrintDialog → _build_statement_html() → _print_html_document() → QPrinter
```

### **Key Features:**
- **High Resolution:** 300 DPI printing
- **A4 Portrait:** Standard page size
- **HTML Rendering:** QTextDocument with HTML/CSS
- **Professional Styling:** Gradient backgrounds, borders, typography
- **Debug Output:** Saves HTML to file for debugging

---

## 📋 **Data Structure & Logic**

### **Transaction Processing:**
```python
# Only shows LATEST sale (not all sales)
latest_sale = session.query(Sale).filter(
    Sale.customer_id == self.customer_id,
    Sale.sale_date >= start_dt,
    Sale.sale_date <= end_dt
).order_by(Sale.sale_date.desc()).first()
```

### **Item-Level Details:**
- **Product Name:** From `item.product.name`
- **Quantity:** From `item.quantity`
- **Unit Price:** From `item.unit_price`
- **Discount:** From `item.discount` (percentage)
- **Final Amount:** Proportionate calculation with discount

### **Financial Calculations:**
- **Total Sales:** `sale.total_amount` (after discounts)
- **Total Discounts:** `sale.discount_amount`
- **Amount Due:** `customer.current_credit` from database

---

## 🎨 **HTML Template Features**

### **Professional Design:**
- **Header:** Shop info, statement period
- **Customer Section:** Bill-to information
- **Table:** 7 columns with alternating row colors
- **Summary:** Gradient cards with totals
- **Footer:** Generation timestamp, thank you message

### **CSS Styling:**
- **Typography:** Segoe UI font, proper sizing
- **Colors:** Professional blue/gray color scheme
- **Layout:** Responsive table, centered content
- **Print Optimization:** Page margins, print-friendly styling

### **Conditional Elements:**
- **Discount Row:** Only shows if `total_discounts > 0`
- **Empty State:** Message when no transactions found
- **Negative Balance:** Red color for amount due

---

## 🔧 **Key Configuration Points**

### **Shop Information Source:**
```python
settings = QSettings()
shop_name = settings.value("business_name", "Sarhad General Store")
shop_address = settings.value("business_address", "Madni Chowk")
shop_phone = settings.value("business_phone", "+923225031977")
```

### **Output Directory:**
```python
self.output_dir = os.path.join(os.getcwd(), "documents")
```

### **Print Settings:**
- **Resolution:** 300 DPI
- **Page Size:** A4
- **Orientation:** Portrait
- **Margins:** 12.7mm (top/bottom), 18mm (bottom)

---

## 🚨 **Important Notes**

### **Current Limitations:**
1. **Latest Sale Only:** Shows only the most recent sale, not complete history
2. **No Payment Details:** Payment rows are empty in HTML output
3. **Fixed Date Range:** Default is last 3 months
4. **Single Customer:** One statement per dialog

### **Debug Features:**
- **HTML Debug File:** Saves HTML to `debug_statement_*.html`
- **Console Logging:** Extensive debug output in console
- **Error Handling:** Try-catch blocks with rollback

### **Data Dependencies:**
- **Customer Table:** `current_credit` field for amount due
- **Sales Table:** `total_amount`, `discount_amount` fields
- **Sale Items Table:** Product relationships for item details
- **Payments Table:** Payment records (excluded from HTML display)

---

## 📁 **File Locations & Dependencies**

### **Core Files:**
- `views/customer_statement.py` - Main statement dialog
- `views/customers.py` - Customer management UI
- `views/main_window.py` - Signal routing
- `models/database.py` - Data models (Customer, Sale, SaleItem, Payment)

### **Generated Files:**
- `documents/customer_statement_[id]_[timestamp].pdf` - Exported PDFs
- `debug_statement_[timestamp].html` - Debug HTML files

### **Settings Dependencies:**
- `business_name` - Shop name
- `business_address` - Shop address  
- `business_phone` - Shop phone number

---

## 🎯 **Usage Flow Summary**

1. **User Action:** Click "📄 Statement" button in customer list
2. **Signal Emission:** `action_export_statement.emit(customer_id)`
3. **Dialog Creation:** `CustomerStatementDialog(controllers, customer_id)`
4. **Data Loading:** Customer info, latest sale, payments
5. **HTML Generation:** Professional statement template
6. **User Choice:** Export PDF or Print dialog
7. **Output:** High-quality PDF/printed statement

---

## 🔍 **Recent Customer Statements Found**

The system has generated multiple customer statements:
- `customer_statement_2_20251227_195136.pdf`
- `customer_statement_3_20251228_185534.pdf` 
- `customer_statement_61_20260114_155431.pdf`
- `customer_statement_61_20260114_155507.pdf`

These indicate the system is actively used for customer billing and statement generation.
