"""Tests for crash reporting system"""
import pytest
from PySide6.QtWidgets import QApplication
from pos_app.views.sales_wrapper import SafeSalesWidget
from pos_app.utils.crash_reporter import crash_reporter

@pytest.fixture
def qt_app():
    """Fixture providing QApplication instance"""
    app = QApplication([])
    yield app
    app.quit()

def test_crash_reporting(qt_app, tmp_path):
    """Verify crashes are properly reported"""
    # Setup crash reporter with test directory
    crash_reporter.log_file = tmp_path / "test_crashes.log"
    
    # Create widget with invalid controller that will crash
    class CrashController:
        def create_sale(self, *args):
            raise ValueError("Test crash")
            
    # This should trigger our crash reporter
    widget = SafeSalesWidget(CrashController())
    with pytest.raises(ValueError):
        widget.process_sale()
    
    # Verify crash was logged
    assert crash_reporter.log_file.exists()
    log_content = crash_reporter.log_file.read_text()
    assert "CRASH" in log_content
    assert "process_sale" in log_content
    assert "Test crash" in log_content
