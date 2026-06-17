"""
ADVANCED ANALYTICS CENTER - PART 2: UI COMPONENTS AND REPORTS
Continuation of comprehensive implementation with 10000+ lines
"""

# Import required SQL functions
from sqlalchemy import func
import traceback


class GlassCard(QFrame):
    """Enhanced glassmorphic card with animations and interactions"""
    
    clicked = Signal(str)
    hover_enter = Signal(str)
    hover_leave = Signal(str)
    
    def __init__(self, title: str, icon: str = "📊", subtitle: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.icon = icon
        self.subtitle = subtitle
        self.setup_ui()
        self.setup_animations()
        self.setup_effects()
        
    def setup_ui(self):
        """Setup enhanced card UI"""
        self.setFixedHeight(280)
        self.setMinimumWidth(340)
        self.setCursor(Qt.PointingHandCursor)
        
        # Main layout with margins
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header section
        header_layout = QHBoxLayout()
        
        # Icon with animation
        self.icon_label = QLabel(self.icon)
        self.icon_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(59, 130, 246, 0.3), stop:1 rgba(147, 51, 234, 0.3));
                border-radius: 16px;
                padding: 12px;
            }
        """)
        header_layout.addWidget(self.icon_label)
        
        # Title section
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: 700;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
        """)
        title_layout.addWidget(self.title_label)
        
        if self.subtitle:
            self.subtitle_label = QLabel(self.subtitle)
            self.subtitle_label.setStyleSheet("""
                QLabel {
                    color: rgba(255, 255, 255, 0.6);
                    font-size: 12px;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                }
            """)
            title_layout.addWidget(self.subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("""
            QLabel {
                color: #4ade80;
                font-size: 16px;
            }
        """)
        header_layout.addWidget(self.status_indicator)
        
        layout.addLayout(header_layout)
        
        # KPIs section
        self.kpi_widget = QWidget()
        self.kpi_layout = QVBoxLayout(self.kpi_widget)
        self.kpi_layout.setSpacing(8)
        layout.addWidget(self.kpi_widget)
        
        # Progress bar (optional)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                height: 6px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #8b5cf6);
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Footer with trend
        self.footer_widget = QWidget()
        self.footer_layout = QHBoxLayout(self.footer_widget)
        self.footer_layout.setContentsMargins(0, 8, 0, 0)
        
        self.trend_label = QLabel("")
        self.trend_label.setStyleSheet("""
            QLabel {
                color: #4ade80;
                font-size: 12px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
        """)
        self.footer_layout.addWidget(self.trend_label)
        
        self.footer_layout.addStretch()
        
        self.action_button = QPushButton("View Details →")
        self.action_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                padding: 6px 12px;
                color: rgba(255, 255, 255, 0.8);
                font-size: 11px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border-color: rgba(255, 255, 255, 0.4);
                color: white;
            }
        """)
        self.action_button.clicked.connect(lambda: self.clicked.emit(self.title))
        self.footer_layout.addWidget(self.action_button)
        
        layout.addWidget(self.footer_widget)
        
    def setup_animations(self):
        """Setup advanced animations"""
        # Fade-in animation
        self.fade_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.fade_effect)
        
        self.fade_animation = QPropertyAnimation(self.fade_effect, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Hover scale animation
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(200)
        self.scale_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Icon rotation animation
        self.icon_rotation = QPropertyAnimation(self.icon_label, b"rotation")
        self.icon_rotation.setDuration(500)
        self.icon_rotation.setEasingCurve(QEasingCurve.InOutCubic)
        
    def setup_effects(self):
        """Setup visual effects"""
        # Drop shadow effect
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(20)
        self.shadow_effect.setXOffset(0)
        self.shadow_effect.setYOffset(4)
        self.shadow_effect.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(self.shadow_effect)
        
    def enterEvent(self, event):
        """Handle mouse enter with enhanced effects"""
        # Scale animation
        current_rect = self.geometry()
        new_rect = current_rect.adjusted(-8, -8, 16, 16)
        self.scale_animation.setStartValue(current_rect)
        self.scale_animation.setEndValue(new_rect)
        self.scale_animation.start()
        
        # Icon rotation
        self.icon_rotation.setStartValue(0)
        self.icon_rotation.setEndValue(360)
        self.icon_rotation.start()
        
        # Update shadow
        self.shadow_effect.setBlurRadius(30)
        self.shadow_effect.setYOffset(8)
        
        # Emit signal
        self.hover_enter.emit(self.title)
        
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave"""
        # Reverse scale animation
        current_rect = self.geometry()
        original_rect = current_rect.adjusted(8, 8, -16, -16)
        self.scale_animation.setStartValue(current_rect)
        self.scale_animation.setEndValue(original_rect)
        self.scale_animation.start()
        
        # Reset shadow
        self.shadow_effect.setBlurRadius(20)
        self.shadow_effect.setYOffset(4)
        
        # Emit signal
        self.hover_leave.emit(self.title)
        
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        """Handle mouse click with visual feedback"""
        # Pulse animation on click
        self.icon_rotation.setStartValue(0)
        self.icon_rotation.setEndValue(180)
        self.icon_rotation.start()
        
        self.clicked.emit(self.title)
        super().mousePressEvent(event)
        
    def showEvent(self, event):
        """Animate on show with staggered effect"""
        # Staggered animation for multiple cards
        QTimer.singleShot(50, self.fade_animation.start)
        super().showEvent(event)
        
    def update_kpis(self, primary_value: str, secondary_value: str = "", 
                    trend: str = "", progress: int = 0):
        """Update KPI values with animations"""
        # Clear existing KPIs
        for i in reversed(range(self.kpi_layout.count())):
            child = self.kpi_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Primary KPI
        primary_label = QLabel(primary_value)
        primary_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: 800;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(59, 130, 246, 0.2), stop:1 rgba(147, 51, 234, 0.2));
                border-radius: 8px;
                padding: 8px 12px;
            }
        """)
        self.kpi_layout.addWidget(primary_label)
        
        # Secondary KPI
        if secondary_value:
            secondary_label = QLabel(secondary_value)
            secondary_label.setStyleSheet("""
                QLabel {
                    color: rgba(255, 255, 255, 0.7);
                    font-size: 14px;
                    font-weight: 500;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                }
            """)
            self.kpi_layout.addWidget(secondary_label)
        
        # Update trend
        if trend:
            color = "#4ade80" if "+" in trend else "#f87171"
            self.trend_label.setText(trend)
            self.trend_label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-size: 12px;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                    font-weight: 600;
                }}
            """)
        
        # Update progress
        if progress > 0:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(progress)
        else:
            self.progress_bar.setVisible(False)
            
    def set_status(self, status: str):
        """Set status indicator"""
        colors = {
            "good": "#4ade80",
            "warning": "#f59e0b", 
            "error": "#ef4444",
            "neutral": "#6b7280"
        }
        color = colors.get(status, "#6b7280")
        self.status_indicator.setStyleSheet(f"QLabel {{ color: {color}; font-size: 16px; }}")


class InteractiveDataTable(QTableWidget):
    """Advanced data table with sorting, filtering, and export capabilities"""
    
    data_exported = Signal(dict)
    row_selected = Signal(int)
    cell_double_clicked = Signal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_data = []
        self.filtered_data = []
        self.sort_column = -1
        self.sort_order = Qt.AscendingOrder
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup table UI"""
        # Enhanced styling
        self.setStyleSheet("""
            QTableWidget {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                gridline-color: rgba(255, 255, 255, 0.05);
                selection-background-color: rgba(59, 130, 246, 0.3);
                selection-color: white;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            QTableWidget::item:selected {
                background: rgba(59, 130, 246, 0.3);
            }
            QHeaderView::section {
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-right: 1px solid rgba(255, 255, 255, 0.05);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                padding: 12px;
                font-weight: 600;
                color: white;
            }
            QHeaderView::section:hover {
                background: rgba(255, 255, 255, 0.15);
            }
        """)
        
        # Table properties
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setShowGrid(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setDefaultSectionSize(150)
        
        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def setup_connections(self):
        """Setup signal connections"""
        self.itemSelectionChanged.connect(self.on_selection_changed)
        self.cellDoubleClicked.connect(self.cell_double_clicked.emit)
        self.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        
    def load_data(self, data: List[Dict], headers: List[str]):
        """Load data into table"""
        self.original_data = data
        self.filtered_data = data.copy()
        
        # Set headers
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # Load data
        self.setRowCount(len(data))
        for row, row_data in enumerate(data):
            for col, header in enumerate(headers):
                value = row_data.get(header, "")
                item = QTableWidgetItem(str(value))
                item.setData(Qt.UserRole, row_data)  # Store full row data
                self.setItem(row, col, item)
        
        # Auto-adjust columns
        self.resizeColumnsToContents()
        
    def filter_data(self, filter_text: str, column: int = -1):
        """Filter table data"""
        if not filter_text:
            self.filtered_data = self.original_data.copy()
        else:
            filter_text = filter_text.lower()
            self.filtered_data = []
            
            for row_data in self.original_data:
                if column >= 0:
                    # Filter specific column
                    header = self.horizontalHeaderItem(column).text()
                    value = str(row_data.get(header, "")).lower()
                    if filter_text in value:
                        self.filtered_data.append(row_data)
                else:
                    # Filter all columns
                    for value in row_data.values():
                        if filter_text in str(value).lower():
                            self.filtered_data.append(row_data)
                            break
        
        # Reload filtered data
        headers = [self.horizontalHeaderItem(i).text() for i in range(self.columnCount())]
        self.load_data(self.filtered_data, headers)
        
    def sort_data(self, column: int, order: Qt.SortOrder):
        """Sort table data"""
        if column < 0 or column >= self.columnCount():
            return
            
        header = self.horizontalHeaderItem(column).text()
        
        # Sort filtered data
        self.filtered_data.sort(key=lambda x: self._get_sort_key(x.get(header, "")), 
                              reverse=(order == Qt.DescendingOrder))
        
        # Reload data
        headers = [self.horizontalHeaderItem(i).text() for i in range(self.columnCount())]
        self.load_data(self.filtered_data, headers)
        
        # Update sort indicators
        self.horizontalHeader().setSortIndicator(column, order)
        
    def _get_sort_key(self, value):
        """Get sort key for different data types"""
        try:
            # Try to convert to number
            if isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                return float(value)
            return str(value).lower()
        except:
            return str(value).lower()
            
    def export_data(self, format_type: str = "CSV"):
        """Export table data"""
        headers = [self.horizontalHeaderItem(i).text() for i in range(self.columnCount())]
        data = []
        
        for row in range(self.rowCount()):
            row_data = {}
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item:
                    header = headers[col]
                    row_data[header] = item.text()
            data.append(row_data)
        
        export_data = {
            'headers': headers,
            'data': data,
            'format': format_type
        }
        
        self.data_exported.emit(export_data)
        
    def show_context_menu(self, position):
        """Show context menu"""
        menu = QMenu(self)
        
        # Copy action
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(self.copy_selection)
        
        # Export actions
        export_menu = menu.addMenu("Export")
        
        csv_action = export_menu.addAction("Export as CSV")
        csv_action.triggered.connect(lambda: self.export_data("CSV"))
        
        excel_action = export_menu.addAction("Export as Excel")
        excel_action.triggered.connect(lambda: self.export_data("Excel"))
        
        json_action = export_menu.addAction("Export as JSON")
        json_action.triggered.connect(lambda: self.export_data("JSON"))
        
        menu.addSeparator()
        
        # Filter actions
        filter_action = menu.addAction("Filter...")
        filter_action.triggered.connect(self.show_filter_dialog)
        
        clear_filter_action = menu.addAction("Clear Filter")
        clear_filter_action.triggered.connect(lambda: self.filter_data(""))
        
        menu.exec_(self.mapToGlobal(position))
        
    def copy_selection(self):
        """Copy selected data to clipboard"""
        selected_items = self.selectedItems()
        if not selected_items:
            return
            
        clipboard = QApplication.clipboard()
        text_data = ""
        
        # Get selected rows
        rows = set(item.row() for item in selected_items)
        
        for row in sorted(rows):
            row_data = []
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            text_data += "\t".join(row_data) + "\n"
        
        clipboard.setText(text_data.strip())
        
    def show_filter_dialog(self):
        """Show filter dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Filter Data")
        dialog.setFixedSize(400, 200)
        
        layout = QVBoxLayout(dialog)
        
        # Column selection
        column_layout = QHBoxLayout()
        column_layout.addWidget(QLabel("Column:"))
        
        column_combo = QComboBox()
        headers = [self.horizontalHeaderItem(i).text() for i in range(self.columnCount())]
        column_combo.addItems(["All Columns"] + headers)
        column_layout.addWidget(column_combo)
        
        layout.addLayout(column_layout)
        
        # Filter text
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        
        filter_input = QLineEdit()
        filter_layout.addWidget(filter_input)
        
        layout.addLayout(filter_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(lambda: self.apply_filter(column_combo.currentIndex() - 1, filter_input.text()))
        button_layout.addWidget(apply_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
        
    def apply_filter(self, column: int, filter_text: str):
        """Apply filter from dialog"""
        self.filter_data(filter_text, column)
        
    def on_selection_changed(self):
        """Handle selection change"""
        selected_items = self.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            self.row_selected.emit(row)
            
    def on_header_clicked(self, column: int):
        """Handle header click for sorting"""
        if self.sort_column == column:
            # Toggle sort order
            self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            # New column, default to ascending
            self.sort_column = column
            self.sort_order = Qt.AscendingOrder
            
        self.sort_data(column, self.sort_order)


class AdvancedChartWidget(QWidget):
    """Advanced chart widget with multiple chart types and interactions"""
    
    chart_clicked = Signal(str, dict)
    export_requested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chart_renderer = ChartRenderer()
        self.current_chart = None
        self.chart_data = {}
        self.chart_type = "line"
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup chart widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Chart controls
        controls_layout = QHBoxLayout()
        
        # Chart type selector
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["Line", "Bar", "Pie", "Area", "Scatter", "Heatmap"])
        self.chart_type_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                padding: 6px 12px;
                color: white;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid rgba(255, 255, 255, 0.6);
            }
        """)
        controls_layout.addWidget(QLabel("Chart Type:"))
        controls_layout.addWidget(self.chart_type_combo)
        
        controls_layout.addStretch()
        
        # Export button
        export_btn = QPushButton("Export Chart")
        export_btn.setStyleSheet("""
            QPushButton {
                background: rgba(59, 130, 246, 0.2);
                border: 1px solid rgba(59, 130, 246, 0.4);
                border-radius: 6px;
                padding: 6px 12px;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(59, 130, 246, 0.3);
                border-color: rgba(59, 130, 246, 0.6);
            }
        """)
        export_btn.clicked.connect(self.export_chart)
        controls_layout.addWidget(export_btn)
        
        layout.addLayout(controls_layout)
        
        # Chart container
        self.chart_container = QWidget()
        self.chart_container.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
        """)
        
        self.chart_layout = QVBoxLayout(self.chart_container)
        self.chart_layout.setContentsMargins(20, 20, 20, 20)
        
        layout.addWidget(self.chart_container)
        
    def setup_connections(self):
        """Setup signal connections"""
        self.chart_type_combo.currentTextChanged.connect(self.update_chart_type)
        
    def set_data(self, data: Dict, chart_type: str = "line", title: str = "", 
                 x_label: str = "", y_label: str = ""):
        """Set chart data and render"""
        self.chart_data = data
        self.chart_type = chart_type
        
        if not data:
            self.show_empty_chart("No data available")
            return
            
        self.render_chart(title, x_label, y_label)
        
    def render_chart(self, title: str = "", x_label: str = "", y_label: str = ""):
        """Render chart based on type"""
        # Clear existing chart
        for i in reversed(range(self.chart_layout.count())):
            child = self.chart_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Create chart based on type
        if self.chart_type.lower() == "line":
            canvas = self.chart_renderer.create_line_chart(self.chart_data, title, x_label, y_label)
        elif self.chart_type.lower() == "bar":
            canvas = self.chart_renderer.create_bar_chart(self.chart_data, title, x_label, y_label)
        elif self.chart_type.lower() == "pie":
            canvas = self.chart_renderer.create_pie_chart(self.chart_data, title)
        elif self.chart_type.lower() == "area":
            canvas = self.chart_renderer.create_area_chart(self.chart_data, title, x_label, y_label)
        elif self.chart_type.lower() == "scatter":
            canvas = self.chart_renderer.create_scatter_chart(self.chart_data, title, x_label, y_label)
        elif self.chart_type.lower() == "heatmap":
            canvas = self.chart_renderer.create_heatmap(self.chart_data, title, x_label, y_label)
        else:
            canvas = self.chart_renderer.create_line_chart(self.chart_data, title, x_label, y_label)
        
        # Add navigation toolbar
        toolbar = NavigationToolbar(canvas, self)
        toolbar.setStyleSheet("""
            QToolBar {
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 6px;
                padding: 4px;
            }
            QToolButton {
                background: transparent;
                border: none;
                padding: 4px;
                color: white;
            }
            QToolButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
        """)
        
        self.chart_layout.addWidget(toolbar)
        self.chart_layout.addWidget(canvas)
        
        self.current_chart = canvas
        
    def show_empty_chart(self, message: str):
        """Show empty chart with message"""
        for i in reversed(range(self.chart_layout.count())):
            child = self.chart_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        empty_label = QLabel(message)
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.5);
                font-size: 16px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                padding: 40px;
            }
        """)
        
        self.chart_layout.addWidget(empty_label)
        
    def update_chart_type(self, chart_type: str):
        """Update chart type"""
        self.chart_type = chart_type
        self.render_chart()
        
    def export_chart(self):
        """Export chart"""
        if self.current_chart:
            self.export_requested.emit(self.chart_type)


# Continue with more components...
