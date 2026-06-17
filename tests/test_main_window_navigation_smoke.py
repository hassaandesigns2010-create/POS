import pytest


@pytest.mark.ui
def test_main_window_page_navigation_smoke(qtbot, db_session):
    """Open MainWindow and navigate key pages to ensure no exceptions in offline/empty DB."""
    # IMPORTANT:
    # MainWindow and some widgets may indirectly use the global SQLAlchemy engine/session
    # configured in pos_app.models.database (which can default to PostgreSQL). To ensure this
    # smoke test runs on any machine, force an in-memory SQLite engine/session here.
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, scoped_session

    # Avoid modal dialogs blocking the test run
    try:
        from PySide6.QtWidgets import QMessageBox
    except ImportError:
        from PyQt6.QtWidgets import QMessageBox

    def _noop(*_args, **_kwargs):
        return QMessageBox.StandardButton.Ok if hasattr(QMessageBox, 'StandardButton') else QMessageBox.Ok

    for attr in ("information", "warning", "critical", "question"):
        try:
            setattr(QMessageBox, attr, staticmethod(_noop))
        except Exception:
            pass

    from types import SimpleNamespace
    from pos_app.models.database import Base
    from pos_app.controllers.business_logic import BusinessController
    from pos_app.views.main_window import MainWindow

    # Preserve global DB objects to avoid leaking state to other tests.
    try:
        import pos_app.models.database as mdb
        _old_engine = getattr(mdb, 'engine', None)
        _old_sessionlocal = getattr(mdb, 'SessionLocal', None)
        _old_db_session = getattr(mdb, 'db_session', None)
    except Exception:
        mdb = None
        _old_engine = _old_sessionlocal = _old_db_session = None

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
        echo=False,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()

    # Ensure global db objects point to our SQLite engine for anything that imports them.
    if mdb is not None:
        try:
            mdb.engine = engine
            mdb.SessionLocal = SessionLocal
            mdb.db_session = scoped_session(SessionLocal)
        except Exception:
            pass

    try:
        business = BusinessController(session)
        controllers = {
            'inventory': business,
            'customers': business,
            'suppliers': business,
            'sales': business,
            'reports': business,
            # Optional: auth controller is not required for navigation
        }

        # Admin user so Settings/Reports are available
        current_user = SimpleNamespace(username='admin', is_admin=True)

        window = MainWindow(controllers, current_user=current_user)
        qtbot.addWidget(window)
        window.show()

        # Navigate key pages
        window._navigate(window.inventory)
        window._navigate(window.sales)
        window._navigate(window.reports)
        window._navigate(window.settings)

        # Process pending UI events
        qtbot.wait(50)

        # Basic assertions: current widget is Settings at the end
        assert window.stacked_widget.currentWidget() is window.settings
    finally:
        try:
            session.close()
        except Exception:
            pass

        # Restore globals
        if mdb is not None:
            try:
                mdb.engine = _old_engine
                mdb.SessionLocal = _old_sessionlocal
                mdb.db_session = _old_db_session
            except Exception:
                pass
