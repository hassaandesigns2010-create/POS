import sys
import os

# Import qt_compat FIRST to patch Qt enums for PyQt6 compatibility
try:
    # Try absolute import first
    import qt_compat
except ImportError:
    try:
        # Try from pos_app package
        from pos_app import qt_compat
    except ImportError:
        print("[ERROR] Could not import qt_compat - ensure qt_compat.py exists in pos_app directory")
        raise

import threading
import time
from datetime import datetime
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import qInstallMessageHandler, QtMsgType
except ImportError:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import qInstallMessageHandler, QtMsgType
import logging
# Ensure console can print Unicode on Windows cmd
try:
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')
except Exception:
    pass
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global exception handler for Qt errors
def handle_qt_exceptions(exception_type, exception_value, exception_traceback):
    """Global exception handler for Qt application"""
    import traceback
    from datetime import datetime
    
    error_msg = f"QT EXCEPTION: {exception_type.__name__}: {exception_value}\n"
    error_msg += f"Timestamp: {datetime.now()}\n"
    error_msg += f"Traceback:\n{''.join(traceback.format_exception(exception_type, exception_value, exception_traceback))}"
    
    # Log to file
    try:
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        logs_dir = os.path.join(base_dir, 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)
        
        error_log_path = os.path.join(logs_dir, 'qt_errors.log')
        with open(error_log_path, 'a', encoding='utf-8') as f:
            f.write(error_msg + "\n" + "="*80 + "\n")
        print(f"[QT_ERROR] Qt error logged to: {error_log_path}")
    except Exception as log_error:
        print(f"[QT_ERROR] Could not write Qt error log: {log_error}")
    
    print(error_msg)

# Install global exception handler
sys.excepthook = handle_qt_exceptions

# Add the parent directory to Python path so we can import pos_app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from pos_app.views.main_window import MainWindow
from pos_app.views.login import LoginDialog
from pos_app.controllers.safe_business_controller import SafeBusinessController as BusinessController
from pos_app.utils.logger import app_logger
from pos_app.utils.network_manager import bootstrap_database_config, set_server_mode, set_client_mode
from pos_app.utils.license_manager import LicenseManager
from pos_app.utils.startup_validator import StartupValidator
from pos_app.views.sales_wrapper import SafeSalesWidget as SalesWidget

# Import crash prevention system
try:
    from pos_app.utils.crash_prevention import initialize_crash_prevention
    crash_prevention = initialize_crash_prevention()
    print("[STARTUP] Crash prevention system initialized")
except Exception as e:
    print(f"[WARN] Could not initialize crash prevention: {e}")

# Import unified logger and watchdog
from pos_app.utils.unified_logger import unified_logger
from pos_app.utils.unresponsive_monitor import initialize_watchdog

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    Catch-all for any unhandled exceptions.
    Logs to the unified system AND shows a dialog.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Format traceback
    tb = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # Log to the unified log file
    logging.critical(f"FATAL UNHANDLED EXCEPTION:\n{tb}")
    
    # Also log to a dedicated crash file for easy identification
    try:
        with open("f:/pos_app/logs/CRITICAL_CRASH.txt", "a") as f:
            f.write(f"\n{'='*50}\n{datetime.now()}\n{tb}\n{'='*50}\n")
    except:
        pass

    # Show user-friendly error dialog
    try:
        from PySide6.QtWidgets import QMessageBox
        app = QApplication.instance()
        if app:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("A critical error occurred.")
            msg.setInformativeText(f"The details have been logged. You may need to restart the application.\n\nError: {str(exc_value)}")
            msg.setWindowTitle("System Error")
            # Ensure it doesn't block forever
            QTimer.singleShot(30000, msg.close) 
            msg.exec()
    except:
        # If UI fails, at least we logged it
        pass

# Set the global exception handler
sys.excepthook = global_exception_handler

def _install_dialog_auto_fit(app: QApplication):
    try:
        try:
            from PySide6.QtCore import QObject, QEvent
            from PySide6.QtWidgets import QDialog
        except ImportError:
            from PyQt6.QtCore import QObject, QEvent
            from PyQt6.QtWidgets import QDialog

        class _DialogAutoFitFilter(QObject):
            def eventFilter(self, obj, event):
                try:
                    if not isinstance(obj, QDialog):
                        return False

                    try:
                        t = event.type()
                    except Exception:
                        return False

                    try:
                        show_t = QEvent.Type.Show
                    except Exception:
                        show_t = getattr(QEvent, 'Show', None)

                    if show_t is None or t != show_t:
                        return False

                    # Only apply once per dialog instance
                    try:
                        if bool(obj.property('_auto_fit_done')):
                            return False
                    except Exception:
                        pass

                    try:
                        obj.setProperty('_auto_fit_done', True)
                    except Exception:
                        pass

                    try:
                        scr = obj.screen() if hasattr(obj, 'screen') else None
                        if scr is None and hasattr(app, 'primaryScreen'):
                            scr = app.primaryScreen()
                        if scr is None:
                            return False

                        geo = scr.availableGeometry()

                        # Ensure dialog is not forced fullscreen/maximized
                        try:
                            obj.showNormal()
                        except Exception:
                            pass

                        # Let layouts compute a natural size first
                        try:
                            obj.adjustSize()
                        except Exception:
                            pass

                        # Cap size to 80% of available screen
                        try:
                            max_w = int(geo.width() * 0.8)
                            max_h = int(geo.height() * 0.8)
                        except Exception:
                            max_w = geo.width()
                            max_h = geo.height()

                        try:
                            w = obj.width()
                            h = obj.height()
                            # Keep natural size; only clamp down if too large
                            if w > max_w or h > max_h:
                                obj.resize(min(w, max_w), min(h, max_h))
                        except Exception:
                            pass

                        # Center dialog on screen
                        try:
                            x = geo.x() + (geo.width() - obj.width()) // 2
                            y = geo.y() + (geo.height() - obj.height()) // 2
                            obj.move(x, y)
                        except Exception:
                            pass

                        # Re-run layout after resize
                        try:
                            obj.updateGeometry()
                        except Exception:
                            pass
                    except Exception:
                        return False

                except Exception:
                    return False

                return False

        f = _DialogAutoFitFilter(app)
        app.installEventFilter(f)
        try:
            app._dialog_auto_fit_filter = f
        except Exception:
            pass
    except Exception:
        return


def setup_controllers(db):
    # Instantiate controllers for their respective views
    business = BusinessController(db.session)
    return {
        'inventory': business,
        'customers': business,
        'suppliers': business,
        'sales': business,
        'reports': business
    }

def _is_auto_login_enabled() -> bool:
    """Return True if command-line args or env variable indicate auto-login mode."""
    try:
        for arg in sys.argv[1:]:
            if arg.lower() in ("--no-login", "--auto-login", "nologin"):
                return True
        if os.getenv("POS_AUTO_LOGIN", "0") in ("1", "true", "yes"):
            return True
    except Exception:
        pass
    return False


def setup_folders():
    """Create necessary folders for the application"""
    folders = ['logs', 'documents', 'backups', 'exports']
    for folder in folders:
        path = os.path.join(os.path.dirname(__file__), folder)
        if not os.path.exists(path):
            os.makedirs(path)

def main():
    db = None
    try:
        # Ensure logs directory exists for EXE
        try:
            logs_dir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'logs')
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir, exist_ok=True)
            print(f"[INIT] Logs directory ensured: {logs_dir}")
        except Exception as e:
            print(f"[WARNING] Could not create logs directory: {e}")
        
        # Initialize QSettings organization/application name for persistent settings
        try:
            from PySide6.QtCore import QCoreApplication
        except ImportError:
            from PyQt6.QtCore import QCoreApplication
        QCoreApplication.setOrganizationName("POSSystem")
        QCoreApplication.setApplicationName("POSOffline")
        
        app_mode = 'server'
        # Create necessary folders
        setup_folders()

        # Bootstrap with app_config.json
        try:
            import json
            from pos_app.models.database import update_db_config
            
            # Determine config path - try multiple locations
            # 1. Same directory as executable (for packaged EXE)
            # 2. pos_app/config directory (for development)
            exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            config_path_exe = os.path.join(exe_dir, 'app_config.json')
            config_path_dev = os.path.join(os.path.dirname(__file__), 'config', 'app_config.json')
            
            # Use exe directory if running as packaged app
            if getattr(sys, 'frozen', False):
                config_path = config_path_exe
            else:
                config_path = config_path_dev
            
            app_config = {
                'use_static_ip': False,
                'static_ip': 'localhost',
                'mode': 'server'
            }
            
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        app_config = json.load(f)
                    print(f"[BOOTSTRAP] Loaded app_config.json: mode={app_config.get('mode')}, use_static_ip={app_config.get('use_static_ip')}")
                except Exception as e:
                    print(f"[BOOTSTRAP] Error reading app_config.json: {e}, using defaults")
            else:
                print(f"[BOOTSTRAP] app_config.json not found at {config_path}, creating with defaults")
                # Create config file with defaults
                try:
                    os.makedirs(os.path.dirname(config_path), exist_ok=True)
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(app_config, f, indent=2)
                    print(f"[BOOTSTRAP] Created app_config.json at {config_path}")
                except Exception as e:
                    print(f"[BOOTSTRAP] Error creating app_config.json: {e}")
            
            # Determine host based on config
            mode = app_config.get('mode', 'server').lower()
            app_mode = mode
            use_static_ip = app_config.get('use_static_ip', False)
            static_ip = app_config.get('static_ip', 'localhost')
            
            if use_static_ip and static_ip:
                host = static_ip
                print(f"[BOOTSTRAP] Using static IP: {host}")
            else:
                host = 'localhost'
                print(f"[BOOTSTRAP] Using localhost (static_ip disabled)")
            
            # Configure based on mode
            if mode == 'server':
                print(f"[BOOTSTRAP] Configuring as SERVER mode")
                update_db_config(
                    host=host,
                    port='5432',
                    database='pos_network',
                    username='admin',
                    password='admin'
                )
            elif mode == 'client':
                print(f"[BOOTSTRAP] Configuring as CLIENT mode")
                update_db_config(
                    host=host,
                    port='5432',
                    database='pos_network',
                    username='admin',
                    password='admin'
                )
                # Product cache will be done after DB session is created (below), using that live session.
            else:
                print(f"[BOOTSTRAP] Unknown mode '{mode}', defaulting to server")
                update_db_config(
                    host=host,
                    port='5432',
                    database='pos_network',
                    username='admin',
                    password='admin'
                )
        except Exception as e:
            print(f"[BOOTSTRAP] Error during bootstrap: {e}")
            # Fallback to localhost
            try:
                from pos_app.models.database import update_db_config
                update_db_config(
                    host="localhost",
                    port="5432",
                    database="pos_network",
                    username="admin",
                    password="admin"
                )
            except Exception as e2:
                print(f"[BOOTSTRAP] Error setting fallback config: {e2}")

        # Initialize database connection for the GUI
        from pos_app.database.connection import Database
        db = Database()  # PostgreSQL connection
        
        if db._is_offline:
            print("[WARN] Application will run in OFFLINE MODE")
        else:
            print("[SUCCESS] Database connection established")

            # Client machines: after connecting, download products and cache locally for offline use.
            try:
                if str(app_mode or '').lower() == 'client':
                    from pos_app.data.products import cache_products_from_session
                    cache_products_from_session(db.session)
                    print("[BOOTSTRAP] Cached products to client machine for offline use")
            except Exception as e:
                print(f"[BOOTSTRAP] Warning: could not cache products on client: {e}")

        # Run startup validation and auto-recovery BEFORE login dialog
        # Always run startup validation so schema mismatches are fixed even in offline (SQLite) mode
        try:
            print("[STARTUP] Running pre-login database validation (offline_mode=%s)..." % db._is_offline)
            if not StartupValidator.run_full_startup_check(db.session):
                print("[WARN] Startup validation encountered issues but application will continue...")
        except Exception as e:
            print(f"[WARN] Startup validation error: {e}")
        
        # Ensure an admin user exists (skip if offline)
        if not db._is_offline:
            try:
                from pos_app.models.database import User, Base
                from pos_app.utils.auth import hash_password
                
                # Create tables if they don't exist
                try:
                    Base.metadata.create_all(db.engine)
                except Exception as e:
                    print(f"[WARN] Could not create tables: {e}")
                
                admin_user = db.session.query(User).filter(User.username == 'admin').first()
                if not admin_user:
                    admin = User(
                        username='admin',
                        password_hash=hash_password('admin'),
                        full_name='Administrator',
                        is_admin=True,
                        is_active=True
                    )
                    db.session.add(admin)
                    db.session.commit()
                    print("[SUCCESS] Created default admin user (username: admin, password: admin)")
            except Exception as e:
                print(f"[WARN] Could not ensure admin user exists: {e}")
    except Exception as e:
        print(f"ERROR during initialization: {e}")
        if db:
            db.session.rollback()
        return

    # Skip demo data seeding on startup for speed - load only when needed
    if not db._is_offline:
        print("[STARTUP] Database ready - demo data will load on-demand")
    else:
        print("[OFFLINE] Database is offline")

    # Setup controllers
    controllers = setup_controllers(db)

    # Initialize Qt Application (or get existing instance)
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        _install_dialog_auto_fit(app)
    except Exception:
        pass

    # Install Qt message handler to suppress CSS warnings and log important messages
    def qt_message_handler(mode, context, message):
        # Suppress CSS property warnings
        if any(warning in message.lower() for warning in [
            'unknown property', 'text-shadow', 'box-shadow', 'transform',
            'border-image', 'background-clip', 'filter'
        ]):
            return  # Ignore these warnings
        
        # Log critical and fatal messages
        if mode == QtMsgType.QtCriticalMsg or mode == QtMsgType.QtFatalMsg:
            try:
                if getattr(sys, 'frozen', False):
                    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                else:
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                
                logs_dir = os.path.join(base_dir, 'logs')
                if not os.path.exists(logs_dir):
                    os.makedirs(logs_dir, exist_ok=True)
                
                qt_log_path = os.path.join(logs_dir, 'qt_critical.log')
                from datetime import datetime
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = f"[{timestamp}] Qt Critical ({mode.name}): {message}\n"
                if context:
                    log_entry += f"  File: {context.file}, Line: {context.line}, Function: {context.function}\n"
                
                with open(qt_log_path, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                
                print(f"[QT_CRITICAL] {message}")
            except Exception as e:
                print(f"[ERROR] Could not log Qt critical message: {e}")
        else:
            # Allow other important messages through
            print(f"Qt {mode.name}: {message}")
    
    qInstallMessageHandler(qt_message_handler)
    
    # Apply clean stylesheet to avoid Qt CSS warnings
    try:
        from pos_app.utils.clean_styles import CLEAN_GLOBAL_STYLESHEET
        app.setStyleSheet(CLEAN_GLOBAL_STYLESHEET)
        print(" Clean stylesheet loaded with CSS warning suppression")
    except Exception as e:
        print(f"WARNING: Could not load clean stylesheet: {e}")
        # Don't use fallback stylesheet as it contains problematic CSS
        print("Using minimal styling to avoid CSS warnings")

    # Handle optional auto-login mode
    if _is_auto_login_enabled():
        print("[AUTO-LOGIN] Skipping login dialog – auto login enabled")
        try:
            from pos_app.models.database import User
            from pos_app.utils.auth import hash_password
            
            # Create or get a super admin user for auto-login (not the hardcoded admin)
            super_admin_username = "superadmin"
            super_admin_user = db.session.query(User).filter(User.username == super_admin_username).first()
            
            if not super_admin_user:
                # Create super admin user with proper permissions
                super_admin_user = User(
                    username=super_admin_username,
                    password_hash=hash_password("superadmin123"),
                    full_name="Super Administrator",
                    is_admin=True,
                    is_active=True
                )
                db.session.add(super_admin_user)
                db.session.commit()
                print(f"[AUTO-LOGIN] Created super admin user: {super_admin_username}")
            
            user = super_admin_user
        except Exception as e:
            print(f"[AUTO-LOGIN] Error creating super admin: {e}")
            user = None
        login_success = True
    else:
        login_dialog = LoginDialog()
        login_success = (login_dialog.exec() == LoginDialog.Accepted)
        user = getattr(login_dialog, 'user', None)

    if login_success:
        # User logged in successfully
        
        # Check PostgreSQL installation and setup
        try:
            from pos_app.views.postgres_setup import is_postgresql_installed, is_database_available, PostgreSQLSetupDialog
            
            # If we are already running in offline mode (SQLite fallback), do not block UI startup
            # with PostgreSQL setup prompts. Users should be able to work offline.
            if getattr(db, '_is_offline', False):
                print("[POSTGRESQL] Offline mode active, skipping PostgreSQL setup checks")
            else:
                # Only check if database is not already available (to avoid data loss)
                if not is_database_available():
                    if not is_postgresql_installed():
                        print("[POSTGRESQL] PostgreSQL not found, showing setup dialog...")
                        setup_dialog = PostgreSQLSetupDialog()
                        if setup_dialog.exec() == PostgreSQLSetupDialog.Accepted:
                            print("[POSTGRESQL] Setup completed, reinitializing database connection...")
                            # Reinitialize database connection after setup
                            from pos_app.database.connection import Database
                            db = Database()
                            if not db._is_offline:
                                print("[SUCCESS] Database connection re-established after PostgreSQL setup")
                            else:
                                # Do not kill the app; remain in offline mode.
                                print("[DATABASE] PostgreSQL setup completed but database connection failed. Continuing in offline mode.")
                        else:
                            # Do not exit; user chose to continue offline.
                            print("[POSTGRESQL] Setup cancelled by user")
                            print("[DATABASE] Continuing in offline mode.")
                    else:
                        print("[POSTGRESQL] PostgreSQL found but database not available. Continuing (offline fallback may be active).")
                else:
                    print("[POSTGRESQL] Database already available, skipping setup")
                
        except Exception as e:
            print(f"[POSTGRESQL] Setup check failed: {e}")
            # Continue anyway - maybe database is already working
        
        # Store logged-in user in controllers if auth controller exists
        try:
            if 'auth' in controllers and user is not None and hasattr(user, 'username'):
                controllers['auth'].current_user = user
        except Exception as e:
            print(f"WARNING: Could not store user in controllers: {e}")

        # Check if user is admin, if not switch to client mode
        try:
            current_user = user
            if current_user is not None and hasattr(current_user, 'is_admin') and not current_user.is_admin:
                # Get server IP from config or use localhost as fallback
                network_config = read_network_config()
                server_ip = network_config.get('server_ip', 'localhost')
                port = network_config.get('port', '5432')
                # Set client mode with current server details
                set_client_mode(server_ip, port)
                print(f"Switched to client mode for non-admin user: {current_user.username}")

                # After switching config to client mode, cache products for offline use.
                try:
                    from pos_app.data.products import cache_products_from_session
                    # Use the existing controller session if available
                    sess = None
                    try:
                        if isinstance(controllers, dict):
                            for _n, c in controllers.items():
                                if hasattr(c, 'session') and getattr(c, 'session', None) is not None:
                                    sess = c.session
                                    break
                    except Exception:
                        sess = None
                    if sess is not None:
                        cache_products_from_session(sess)
                except Exception:
                    pass
        except Exception as e:
            print(f"WARNING: Could not switch to client mode: {e}")
        
        # Create window with the logged-in user
        window = MainWindow(controllers, user)
        
        # Comment out UI auditor for faster startup
        # try:
        #     from pos_app.utils.ui_auditor import UIAuditor
        #     UIAuditor.apply_to(window)
        # except Exception as e:
        #     print(f"WARNING: Could not apply UI auditor: {e}")

        window.show()
        
        # Start watchdog after window is shown
        try:
            initialize_watchdog(app, timeout=3.0)  # Further reduced to 3.0 seconds for faster startup
            logging.info("Watchdog monitor active (3s timeout)")
        except Exception as e:
            logging.error(f"Failed to start watchdog: {e}")
        
        # Start cloud sync for auto-updates and log/backup uploads
        try:
            from pos_app.utils.cloud_sync import start_background_sync
            start_background_sync()
            logging.info("Cloud sync background thread started")
        except Exception as e:
            logging.warning(f"Failed to start cloud sync: {e}")
        
        # Comment out connection monitor for faster startup
        # try:
        #     from pos_app.utils.connection_monitor import initialize_connection_monitor
        #     monitor = initialize_connection_monitor(app)
        #     # Pass controller reference to connection monitor
        #     if 'inventory' in controllers:
        #         monitor.set_controller(controllers['inventory'])
        #     logging.info("Connection monitor active for auto-reload")
        # except Exception as e:
        #     logging.error(f"Failed to start connection monitor: {e}")

        sys.exit(app.exec())
    else:
        # User cancelled login
        print("Login cancelled. Exiting application.")
        sys.exit(0)

def create_main_window():
    """Create and return the main window for external startup scripts"""
    try:
        # Setup database connection
        from pos_app.database.connection import Database
        db = Database()
        
        # Setup controllers
        controllers = setup_controllers(db)
        
        # Create main window
        window = MainWindow(controllers)
        
        # Apply UI auditor if available
        try:
            from pos_app.utils.ui_auditor import UIAuditor
            UIAuditor.apply_to(window)
        except Exception as e:
            print(f"WARNING: Could not apply UI auditor: {e}")
        
        return window
        
    except Exception as e:
        print(f"Error creating main window: {e}")
        traceback.print_exc()
        return None

def check_license(app):
    """Check and validate the application license"""
    license_mgr = LicenseManager()
    
    if not license_mgr.is_license_valid():
        if not license_mgr.show_license_dialog():
            print("A valid license is required to run this application.")
            return False
    return True

if __name__ == "__main__":
    # Create application instance
    app = QApplication(sys.argv)
    
    # Set up global exception handler to prevent silent crashes
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Global exception handler to prevent silent crashes"""
        if issubclass(exc_type, KeyboardInterrupt):
            # Handle KeyboardInterrupt normally
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        import traceback
        from datetime import datetime
        
        error_msg = f"CRITICAL ERROR: {exc_type.__name__}: {exc_value}\n"
        error_msg += f"Timestamp: {datetime.now()}\n"
        error_msg += f"Traceback:\n{''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))}"
        
        # Log to file
        try:
            with open('logs/critical_errors.log', 'a') as f:
                f.write(error_msg + "\n" + "="*80 + "\n")
        except Exception:
            pass
        
        # Show error dialog
        try:
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Critical Error")
            msg.setText("A critical error occurred and the application needs to close.")
            msg.setDetailedText(error_msg)
            msg.exec()
        except Exception:
            pass
        
        print(error_msg)
        sys.exit(1)
    
    # Install global exception handler
    sys.excepthook = handle_exception
    
    # Set up Qt error handling to prevent Qt crashes
    def qt_message_handler(mode, context, message):
        """Handle Qt messages to prevent silent Qt crashes"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if mode == 0:  # QtDebugMsg
                level = "DEBUG"
            elif mode == 1:  # QtWarningMsg
                level = "WARNING"
            elif mode == 2:  # QtCriticalMsg
                level = "CRITICAL"
            elif mode == 3:  # QtFatalMsg
                level = "FATAL"
            else:
                level = "INFO"
            
            log_msg = f"[{timestamp}] QT {level}: {message}\n"
            if context.file:
                log_msg += f"  File: {context.file}, Line: {context.line}\n"
            if context.function:
                log_msg += f"  Function: {context.function}\n"
            
            # Log to file
            try:
                with open('logs/qt_errors.log', 'a') as f:
                    f.write(log_msg + "\n")
            except Exception:
                pass
            
            print(log_msg.strip())
            
            # For fatal Qt errors, show dialog
            if mode == 3:  # QtFatalMsg
                try:
                    from PySide6.QtWidgets import QMessageBox
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Qt Fatal Error")
                    msg.setText("A critical Qt error occurred.")
                    msg.setDetailedText(log_msg)
                    msg.exec()
                except Exception:
                    pass
        except Exception:
            pass
    
    # Install Qt message handler
    try:
        from PySide6.QtCore import qInstallMessageHandler
        qInstallMessageHandler(qt_message_handler)
    except ImportError:
        try:
            from PyQt6.QtCore import qInstallMessageHandler
            qInstallMessageHandler(qt_message_handler)
        except Exception:
            pass
    
    # Set up memory monitoring
    def check_memory_usage():
        """Monitor memory usage to prevent memory-related crashes"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
            
            # Log memory usage every 30 seconds
            if memory_mb > 500:  # Warn if using more than 500MB
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_msg = f"[{timestamp}] MEMORY WARNING: {memory_mb:.1f} MB used\n"
                
                try:
                    with open('logs/memory_usage.log', 'a') as f:
                        f.write(log_msg)
                except Exception:
                    pass
                
                print(log_msg.strip())
                
                # If memory usage is very high, suggest restart
                if memory_mb > 1000:  # Critical: 1GB
                    try:
                        from PySide6.QtWidgets import QMessageBox
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Warning)
                        msg.setWindowTitle("Memory Warning")
                        msg.setText(f"High memory usage detected: {memory_mb:.1f} MB")
                        msg.setInformativeText("Consider restarting the application to prevent crashes.")
                        msg.exec()
                    except Exception:
                        pass
        except Exception:
            pass
    
    # Set up memory monitoring timer
    try:
        from PySide6.QtCore import QTimer
        memory_timer = QTimer()
        memory_timer.timeout.connect(check_memory_usage)
        memory_timer.start(30000)  # Check every 30 seconds
    except Exception:
        pass
    
    try:
        _install_dialog_auto_fit(app)
    except Exception:
        pass
    
    # Check license
    if not check_license(app):
        sys.exit(1)
        
    # If license is valid, proceed with main application
    from pathlib import Path
    Path('logs').mkdir(exist_ok=True)
    from pos_app.utils.crash_reporter import crash_reporter
    crash_reporter.log_file = 'logs/crashes.log'
    print("[INFO] Application started")
    try:
        from pos_app.utils.error_logger import log_info
        log_info("Application started", "STARTUP")
    except Exception:
        pass
    
    # Wrap main execution in try-catch to prevent silent crashes
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        # Handle any uncaught exceptions from main()
        import traceback
        from datetime import datetime
        
        error_msg = f"UNCAUGHT EXCEPTION in main(): {type(e).__name__}: {e}\n"
        error_msg += f"Timestamp: {datetime.now()}\n"
        error_msg += f"Traceback:\n{traceback.format_exc()}"
        
        # Log to file - use correct path for EXE
        try:
            # Get the directory where the EXE is running
            if getattr(sys, 'frozen', False):
                # Running as EXE
                base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            else:
                # Running as script
                base_dir = os.path.dirname(os.path.abspath(__file__))
            
            logs_dir = os.path.join(base_dir, 'logs')
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir, exist_ok=True)
            
            error_log_path = os.path.join(logs_dir, 'critical_errors.log')
            with open(error_log_path, 'a', encoding='utf-8') as f:
                f.write(error_msg + "\n" + "="*80 + "\n")
            print(f"[ERROR] Critical error logged to: {error_log_path}")
        except Exception as log_error:
            print(f"[ERROR] Could not write error log: {log_error}")
        
        # Show error dialog
        try:
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Application Error")
            msg.setText("An unexpected error occurred and the application needs to close.")
            msg.setDetailedText(error_msg)
            msg.exec()
        except Exception:
            pass
        
        print(error_msg)
        sys.exit(1)