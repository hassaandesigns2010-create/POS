import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from pos_app.models.database import get_engine, Base, _load_db_config

class Database:
    def __init__(self):
        """Initialize PostgreSQL database connection"""
        self.engine = None
        self.session = None
        self._is_offline = False
        self._connect_with_retries(max_retries=3)

    def _connect_with_retries(self, max_retries=3):
        """PostgreSQL connection with exponential backoff"""
        for attempt in range(max_retries):
            try:
                self._connect()
                print(f"[PostgreSQL] Connection successful (attempt {attempt+1})")
                return
            except OperationalError as e:
                print(f"[PostgreSQL] Connection failed (attempt {attempt+1}): {str(e)}")
                if attempt == max_retries - 1:
                    self._is_offline = True
                    print("[WARNING] Falling back to offline mode")
                    raise
                time.sleep(2 ** attempt)

    def _connect(self):
        """Set up PostgreSQL database connection"""
        try:
            # Use the lazy-loaded engine from models.database
            self.engine = get_engine()
            
            # Test the connection
            with self.engine.connect() as conn:
                pass  # If we get here, connection is good
            
            # Create tables if they don't exist
            Base.metadata.create_all(self.engine)
            
            # Create session
            Session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
            self.session = Session()

            # Confirm PostgreSQL connection
            cfg = _load_db_config()
            print(f"[OK] Connected to PostgreSQL database ({cfg['username']}@{cfg['host']}:{cfg['port']}/{cfg['database']})")
            self._is_offline = False

        except Exception as e:
            print(f"[WARN] Failed to connect to PostgreSQL database: {e}")
            print("  Application will run in OFFLINE MODE with limited functionality")
            print("  Falling back to local SQLite database for offline mode")
            self._is_offline = True

            # Create a real SQLite engine/session so the app and tests can still function.
            try:
                sqlite_path = os.path.join(os.path.expanduser("~"), "POS_Offline_Data.db")
                self.engine = create_engine(
                    f"sqlite:///{sqlite_path}",
                    echo=False,
                    future=True,
                    connect_args={"check_same_thread": False}
                )
                Base.metadata.create_all(self.engine)
                Session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
                self.session = Session()

                # IMPORTANT: other modules may use the global engine/session from pos_app.models.database.
                # If we don't update those, the app can still try to use PostgreSQL and crash.
                try:
                    import pos_app.models.database as mdb
                    from sqlalchemy.orm import scoped_session
                    mdb.engine = self.engine
                    mdb.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
                    mdb.db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))
                except Exception:
                    pass
            except Exception as e2:
                print(f"[ERROR] Failed to initialize offline SQLite database: {e2}")
                raise

    def commit(self):
        """Commit the current transaction"""
        self.session.commit()

    def rollback(self):
        """Rollback the current transaction"""
        self.session.rollback()

    def close(self):
        """Close the database session"""
        self.session.close()
