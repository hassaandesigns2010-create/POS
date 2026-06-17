import os
import sys
import time
from datetime import datetime

# Add the parent of the workspace root to Python path
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parent_dir = os.path.dirname(workspace_root)
sys.path.insert(0, parent_dir)

from pos_app.database.connection import Database
from pos_app.models.database import get_sync_timestamp, SyncState

print("Starting DB Timer Diagnosis...")

db = Database()
session = db.session

try:
    # Check if SyncState table has entries
    sync_states = session.query(SyncState).all()
    print(f"SyncState entries: {len(sync_states)}")
    for state in sync_states:
        print(f"  Key: {state.sync_key}, Last Changed: {state.last_changed}")
except Exception as e:
    print(f"Error querying SyncState: {e}")
    session.rollback()

print("\nSimulating 10 rapid queries to see transaction / connection behavior:")
for i in range(1, 11):
    ts = get_sync_timestamp(session, 'customers')
    # Check if transaction is open
    is_active = session.is_active
    # In SQLAlchemy, we can check if there is a transaction in progress:
    has_transaction = session.in_transaction()
    print(f"Query #{i}: customers sync timestamp = {ts}, Session active: {is_active}, In transaction: {has_transaction}")
    time.sleep(0.5)

print("\nNow performing a commit and checking transaction state:")
session.commit()
print(f"After commit: Session active: {session.is_active}, In transaction: {session.in_transaction()}")

print("\nNow performing query, rollback and checking transaction state:")
ts = get_sync_timestamp(session, 'customers')
print(f"After query: In transaction: {session.in_transaction()}")
session.rollback()
print(f"After rollback: In transaction: {session.in_transaction()}")
