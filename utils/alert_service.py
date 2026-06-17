"""Service for monitoring crash reports and sending alerts"""
import json
from pathlib import Path
from datetime import datetime
from pos_app.utils.notification_service import NotificationService

class AlertService:
    def __init__(self, config_path="pos_app/config/crash_alerts.json"):
        self.config = self._load_config(config_path)
        self.notifier = NotificationService(self.config)
    
    def _load_config(self, path):
        """Load alert configuration"""
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            return {"critical_levels": ["FATAL", "CRITICAL"]}
    
    def _check_thresholds(self, crash_count, period):
        """Check if crash count exceeds configured thresholds"""
        threshold = self.config.get("alert_thresholds", {}).get(period, float("inf"))
        return crash_count >= threshold
    
    def _send_alerts(self, crash_reports):
        """Send alerts for critical crashes"""
        for report in crash_reports:
            if report["level"] in self.config["critical_levels"]:
                self.notifier.send_email(
                    f"POS Critical Crash: {report['type']}",
                    report["message"]
                )
                self.notifier.send_slack(
                    f"Critical crash detected: {report['type']} at {report['location']}"
                )
    
    def check_crashes(self, log_path):
        """Check crash log with comprehensive error handling"""
        try:
            if not Path(log_path).exists():
                return
            
            # Read and parse crash log
            with open(log_path) as f:
                crashes = [json.loads(line) for line in f if line.strip()]
        
            # Filter critical crashes
            critical = [c for c in crashes if c.get("level") in self.config["critical_levels"]]
        
            # Check thresholds and send alerts
            if self._check_thresholds(len(critical), "hourly"):
                self._send_alerts(critical)
    
        except Exception as e:
            print(f"[ALERT SERVICE ERROR] {e}")
            # Fallback to simple email alert
            self.notifier.send_email(
                "POS Alert Service Failure",
                f"Error processing crash reports: {e}"
            )
